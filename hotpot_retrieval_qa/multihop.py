import dspy
import pydantic
import asyncio
import logging

logger = logging.getLogger(__name__)

# Configuration constants
MAX_CONTEXT_LENGTH = 500000  # Adjust based on your model's context window


def _is_in_async_context():
    try:
        loop = asyncio.get_running_loop()
        return loop is not None
    except RuntimeError:
        return False


def _ensure_dspy_configured():
    try:
        current_lm = dspy.settings.lm
        if current_lm is None:
            raise AttributeError("No language model configured")
        logger.info("DSPy already configured, skipping setup")
    except (AttributeError, RuntimeError):
        logger.info("DSPy not configured, setting up for local use")
        from hotpot_retrieval_qa.dspy_setup import setup_dspy

        setup_dspy()


class QueryResult(pydantic.BaseModel):
    id: str
    score: float


class QueryRewriter(dspy.Signature):
    """
    Rewrite complex questions into a strategic sequence of search queries.

    Consider that you have a limited budget of retrieval hops. Plan your queries
    to gather the most important information first, as you may not use all queries.
    """

    question = dspy.InputField(desc="Complex multi-hop question")
    max_hops = dspy.InputField(desc="Maximum number of retrieval hops available")
    search_queries = dspy.OutputField(
        desc=f"Prioritized list of search queries (max {{max_hops}}), ordered by importance"
    )


class ChunkReranker(dspy.Signature):
    """Rerank retrieved chunks based on relevance to the original question."""

    original_question = dspy.InputField(desc="The user's original question")
    chunks = dspy.InputField(desc="Retrieved document chunks in structured format")
    ranked_chunks: list[QueryResult] = dspy.OutputField(
        desc="Chunks ranked by relevance with scores"
    )


class ContextValidation(dspy.Signature):
    """Validate that an answer is supported by the provided context."""

    question = dspy.InputField()
    context = dspy.InputField()
    answer = dspy.InputField()
    is_supported = dspy.OutputField(
        desc="YES if answer is clearly supported by context, NO if not"
    )
    supporting_evidence = dspy.OutputField(
        desc="Specific quotes from context that support the answer"
    )


class Summarizer(dspy.Signature):
    """Summarize the retrieved chunks into a single chunk."""

    chunks = dspy.InputField(desc="Retrieved document chunks")
    summary = dspy.OutputField(desc="Summary of the retrieved chunks")


class MultiHopReasoning(dspy.Signature):
    """Perform multi-hop reasoning ONLY using the provided context. Do not use external knowledge."""

    question = dspy.InputField(
        desc="Complex question requiring multiple reasoning steps"
    )
    context = dspy.InputField(
        desc="Retrieved and ranked documents - USE ONLY THIS INFORMATION"
    )
    reasoning_steps = dspy.OutputField(
        desc="Step-by-step reasoning process using ONLY the provided context"
    )
    answer = dspy.OutputField(
        desc="Final answer based ONLY on the provided context. If context is insufficient, say 'Cannot answer based on provided context.'"
    )
    confidence = dspy.OutputField(desc="Confidence level: high, medium, or low")


class QA(dspy.Module):
    def __init__(self, retriever, max_hops=3):
        super().__init__()

        if not _is_in_async_context():
            _ensure_dspy_configured()

        self.retriever = retriever
        self.max_hops = max_hops

        self.query_rewriter = dspy.ChainOfThought(QueryRewriter)
        self.reranker = dspy.ChainOfThought(ChunkReranker)
        self.reason = dspy.ChainOfThought(MultiHopReasoning)
        self.summarizer = dspy.ChainOfThought(Summarizer)
        self.validator = dspy.ChainOfThought(ContextValidation)

        self.seen_content = set()

        class FollowUpQuery(dspy.Signature):
            question = dspy.InputField()
            current_info = dspy.InputField()
            queries_used = dspy.InputField(desc="Search queries already executed")
            suggested_queries = dspy.InputField(
                desc="Remaining suggested queries from initial planning"
            )
            next_query = dspy.OutputField(
                desc="Next search query needed (can use suggestions or create new), or 'DONE' if sufficient"
            )

        self.follow_up = dspy.Predict(FollowUpQuery)

    def _normalize_content(self, text):
        return " ".join(text.lower().split())

    def _deduplicate_docs(self, docs):
        unique_docs = []
        for doc in docs:
            normalized = self._normalize_content(doc["document"])
            if normalized not in self.seen_content and len(normalized) > 20:
                unique_docs.append(doc)
                self.seen_content.add(normalized)
        return unique_docs

    def forward(self, question):
        all_context = []
        queries_used = []
        self.seen_content.clear()

        rewrite_result = self.query_rewriter(question=question, max_hops=self.max_hops)

        search_queries = (
            rewrite_result.search_queries.split("\n")
            if isinstance(rewrite_result.search_queries, str)
            else rewrite_result.search_queries
        )

        search_queries = [q.strip() for q in search_queries if q.strip()]
        queries_to_use = search_queries[: self.max_hops]

        current_query = queries_to_use[0] if queries_to_use else question
        remaining_suggestions = queries_to_use[1:] if len(queries_to_use) > 1 else []

        for hop in range(self.max_hops):
            docs = self.retriever.retrieve(current_query, k=10)

            unique_docs = self._deduplicate_docs(docs)

            if not unique_docs:
                logger.info(f"No unique documents found at hop {hop}, stopping early")
                break

            chunks_text = "\n".join(
                [
                    f"ID: {chunk['id']}\nContent: {chunk['content']}\nScore: {chunk['score']}\n"
                    for chunk in [
                        {
                            "id": str(i),
                            "content": doc["document"],
                            "score": doc["score"],
                        }
                        for i, doc in enumerate(docs)
                    ]
                ]
            )

            rerank_result = self.reranker(
                original_question=question, chunks=chunks_text
            )

            try:
                ranked_chunks = rerank_result.ranked_chunks

                if not isinstance(ranked_chunks, list) or not ranked_chunks:
                    logger.warning("Invalid reranking result, using original order")
                    raise ValueError("Invalid ranked_chunks format")

                reordered_docs = []
                for query_result in ranked_chunks[:5]:
                    try:
                        idx = int(query_result.id)
                        if idx < len(docs):
                            reordered_docs.append(docs[idx])
                    except (ValueError, AttributeError) as e:
                        logger.warning(f"Invalid query result format: {e}")
                        continue

                if not reordered_docs:
                    raise ValueError("No valid reordered documents")

                context_text = "\n".join([doc["document"] for doc in reordered_docs])

            except Exception as e:
                logger.warning(f"Reranking parse error: {e}, using original order")
                context_text = "\n".join([doc["document"] for doc in docs[:5]])

            all_context.append(context_text)
            queries_used.append(current_query)

            combined_context = "\n---\n".join(all_context)
            if len(combined_context) > MAX_CONTEXT_LENGTH:
                logger.info(
                    f"Context length ({len(combined_context)}) exceeds limit, summarizing..."
                )
                summary_result = self.summarizer(chunks=combined_context)
                all_context = [summary_result.summary]
                combined_context = summary_result.summary

            follow_up_result = self.follow_up(
                question=question,
                current_info=combined_context,
                queries_used=queries_used,
                suggested_queries=remaining_suggestions,
            )

            if follow_up_result.next_query == "DONE" or hop == self.max_hops - 1:
                break

            current_query = follow_up_result.next_query

            if remaining_suggestions and current_query in remaining_suggestions:
                remaining_suggestions.remove(current_query)

        final_context = "\n---\n".join(all_context)
        result = self.reason(question=question, context=final_context)

        validation = self.validator(
            question=question, context=final_context, answer=result.answer
        )

        return dspy.Prediction(
            question=question,
            queries_used=queries_used,
            rewritten_queries=search_queries,
            reasoning_steps=result.reasoning_steps,
            answer=result.answer,
            confidence=result.confidence,
            num_hops=len(queries_used),
            validation=validation,
        )
