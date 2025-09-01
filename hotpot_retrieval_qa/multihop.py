import dspy
import pydantic
import asyncio
import logging

logger = logging.getLogger(__name__)


def _is_in_async_context():
    """Check if we're running in an async context"""
    try:
        loop = asyncio.get_running_loop()
        return loop is not None
    except RuntimeError:
        return False


def _ensure_dspy_configured():
    """Ensure DSPy is configured, but only if not already done"""
    try:
        # Try to access the current language model
        current_lm = dspy.settings.lm
        if current_lm is None:
            raise AttributeError("No language model configured")
        logger.info("DSPy already configured, skipping setup")
    except (AttributeError, RuntimeError):
        # DSPy not configured, so configure it for local use
        logger.info("DSPy not configured, setting up for local use")
        from hotpot_retrieval_qa.dspy_setup import setup_dspy

        setup_dspy()


class QueryResult(pydantic.BaseModel):
    id: str
    score: float


class QueryRewriter(dspy.Signature):
    """Rewrite complex questions into better search queries for multi-hop reasoning."""

    question = dspy.InputField(desc="Complex multi-hop question")
    search_queries = dspy.OutputField(
        desc="List of 3-5 focused search queries to find relevant information"
    )


class ChunkReranker(dspy.Signature):
    """Rerank retrieved chunks based on relevance to the original question."""

    original_question = dspy.InputField(desc="The user's original question")
    chunks = dspy.InputField(desc="Retrieved document chunks")
    ranked_chunks: list[QueryResult] = dspy.OutputField(
        desc="Chunks ranked by relevance with scores"
    )


class MultiHopReasoning(dspy.Signature):
    """Perform multi-hop reasoning with enhanced context."""

    question = dspy.InputField(
        desc="Complex question requiring multiple reasoning steps"
    )
    context = dspy.InputField(desc="Retrieved and ranked documents")
    reasoning_steps = dspy.OutputField(desc="Step-by-step reasoning process")
    answer = dspy.OutputField(desc="Final answer based on reasoning")
    confidence = dspy.OutputField(desc="Confidence level: high, medium, or low")


class QA(dspy.Module):
    def __init__(self, retriever, max_hops=3):
        super().__init__()

        # Only setup DSPy if we're not in an async context
        # (async contexts should handle their own configuration)
        if not _is_in_async_context():
            _ensure_dspy_configured()

        self.retriever = retriever
        self.max_hops = max_hops

        self.query_rewriter = dspy.ChainOfThought(QueryRewriter)
        self.reranker = dspy.ChainOfThought(ChunkReranker)
        self.reason = dspy.ChainOfThought(MultiHopReasoning)

        class FollowUpQuery(dspy.Signature):
            question = dspy.InputField()
            current_info = dspy.InputField()
            next_query = dspy.OutputField(
                desc="Next search query needed, or 'DONE' if sufficient"
            )

        self.follow_up = dspy.Predict(FollowUpQuery)

    def forward(self, question):
        all_context = []
        queries_used = []

        rewrite_result = self.query_rewriter(question=question)
        search_queries = (
            rewrite_result.search_queries.split("\n")
            if isinstance(rewrite_result.search_queries, str)
            else rewrite_result.search_queries
        )

        initial_query = search_queries[0] if search_queries else question

        for hop in range(self.max_hops):
            docs = self.retriever.retrieve(initial_query, k=10)

            chunks_for_reranking = [
                {"id": str(i), "content": doc["document"], "score": doc["score"]}
                for i, doc in enumerate(docs)
            ]

            rerank_result = self.reranker(
                original_question=question, chunks=str(chunks_for_reranking)
            )

            try:
                ranked_chunks = rerank_result.ranked_chunks

                reordered_docs = []
                for query_result in ranked_chunks[:5]:
                    idx = int(query_result.id)
                    if idx < len(docs):
                        reordered_docs.append(docs[idx])

                context_text = "\n".join([doc["document"] for doc in reordered_docs])

            except Exception as e:
                logger.warning(f"Reranking parse error: {e}, using original order")
                context_text = "\n".join([doc["document"] for doc in docs[:5]])

            all_context.append(context_text)
            queries_used.append(initial_query)

            combined_context = "\n---\n".join(all_context)
            follow_up_result = self.follow_up(
                question=question, current_info=combined_context
            )

            if follow_up_result.next_query == "DONE" or hop == self.max_hops - 1:
                break

            initial_query = follow_up_result.next_query

        final_context = "\n---\n".join(all_context)
        result = self.reason(question=question, context=final_context)

        return dspy.Prediction(
            question=question,
            queries_used=queries_used,
            rewritten_queries=search_queries,
            reasoning_steps=result.reasoning_steps,
            answer=result.answer,
            confidence=result.confidence,
            num_hops=len(queries_used),
        )
