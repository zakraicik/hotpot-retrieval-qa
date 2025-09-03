import dspy
import re
import asyncio
import logging
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import time

logger = logging.getLogger(__name__)


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


class QueryRewriter(dspy.Signature):
    """
    Rewrite complex questions into a strategic sequence of search queries.

    Consider that you have a limited budget of retrieval hops. Plan your queries
    to gather the most important information first, as you may not use all queries.

    Format your output as clean text without numbered lists or prefixes.
    """

    question = dspy.InputField(desc="Complex multi-hop question")
    max_hops = dspy.InputField(desc="Maximum number of retrieval hops available")
    search_queries = dspy.OutputField(
        desc="Prioritized list of search queries (max {max_hops}), ordered by importance. Each query on a new line without numbers or prefixes."
    )
    query_objectives = dspy.OutputField(
        desc="For each query, explain what information it aims to find (same order as search_queries). Each objective on a new line without numbers or prefixes."
    )


class HopProcessor(dspy.Signature):
    """
    Process a complete retrieval hop: summarize evidence, draw conclusions, and plan next steps.

    Note: Chunk ranking is handled by similarity computation outside this step.
    Focus on evidence analysis and planning based on the most relevant chunks provided.
    """

    original_question = dspy.InputField(desc="The original question being answered")
    current_query = dspy.InputField(desc="Current search query being processed")
    query_objective = dspy.InputField(desc="What this query aims to accomplish")
    ranked_context = dspy.InputField(
        desc="Top-ranked document chunks (already reordered by similarity)"
    )
    previous_evidence = dspy.InputField(desc="Evidence summaries from previous hops")
    remaining_queries = dspy.InputField(
        desc="Remaining suggested queries from initial planning"
    )
    hop_number = dspy.InputField(desc="Current hop number (1-indexed)")
    max_hops = dspy.InputField(desc="Maximum hops allowed")

    evidence_summary = dspy.OutputField(
        desc="Concise 1-2 sentence summary of key facts found in the provided ranked chunks"
    )
    hop_conclusion = dspy.OutputField(
        desc="What key information was learned from this hop, or 'No relevant information found' if unsuccessful"
    )

    next_query = dspy.OutputField(
        desc="Next search query needed (can use remaining queries or create new), or 'DONE' if sufficient information gathered"
    )
    next_objective = dspy.OutputField(
        desc="Brief explanation of what the next query aims to find, or 'Complete' if DONE"
    )
    confidence_assessment = dspy.OutputField(
        desc="Assessment: 'sufficient' ONLY if you can definitively answer the original question with current evidence. 'needs_more' if you need additional specific information like capitals, dates, or other details not yet found."
    )


class MultiHopReasoning(dspy.Signature):
    """
    Perform comprehensive multi-hop reasoning using all collected evidence to answer complex questions.

    Connect information across retrieved documents to form logical conclusions.
    Use reasonable inference when the context provides sufficient evidence, even if
    not explicitly stated. Include confidence assessment in your reasoning.
    """

    question = dspy.InputField(
        desc="Complex question requiring multiple reasoning steps"
    )
    context = dspy.InputField(
        desc="All retrieved and ranked documents from multiple search hops"
    )
    queries_used = dspy.InputField(desc="Search queries that were executed")
    evidence_summaries = dspy.InputField(desc="Summaries of evidence found at each hop")

    reasoning_summary = dspy.OutputField(
        desc="Clear explanation of how you connected information from the context, including any reasonable inferences made and confidence assessment"
    )
    answer = dspy.OutputField(
        desc="Final answer based on the provided context and reasonable inferences"
    )
    confidence = dspy.OutputField(desc="Confidence level: high, medium, or low")
    is_answer_supported = dspy.OutputField(
        desc="YES if answer is clearly supported by context, NO if not - acts as built-in validation"
    )


class QA(dspy.Module):
    def __init__(self, retriever, max_hops=3):
        super().__init__()

        if not _is_in_async_context():
            _ensure_dspy_configured()

        self.retriever = retriever
        self.max_hops = max_hops

        self.query_rewriter = dspy.ChainOfThought(QueryRewriter)
        self.hop_processor = dspy.ChainOfThought(HopProcessor)
        self.reason = dspy.ChainOfThought(MultiHopReasoning)

        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=2000,
            ngram_range=(1, 2),
            min_df=1,
            sublinear_tf=True,
        )
        self.vectorizer_fitted = False
        self.seen_content = set()

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

    def _clean_text(self, text):
        if not text:
            return text
        cleaned = re.sub(r"^\d+\.\s*", "", text.strip())
        return cleaned

    def _rank_chunks_by_similarity(self, question, docs, top_k=5):
        """Optimized similarity ranking with better vectorizer reuse."""
        start_time = time.time()

        try:
            if not docs:
                return []

            MAX_DOC_LENGTH = 1000
            doc_texts = [doc["document"][:MAX_DOC_LENGTH] for doc in docs]

            all_texts = [question] + doc_texts

            if self.vectorizer_fitted and len(all_texts) <= 50:
                try:
                    tfidf_matrix = self.vectorizer.transform(all_texts)
                except:
                    tfidf_matrix = self.vectorizer.fit_transform(all_texts)
                    self.vectorizer_fitted = True
            else:
                tfidf_matrix = self.vectorizer.fit_transform(all_texts)
                self.vectorizer_fitted = True

            question_vector = tfidf_matrix[0:1]
            doc_vectors = tfidf_matrix[1:]

            similarities = cosine_similarity(question_vector, doc_vectors).flatten()

            ranked_indices = np.argsort(similarities)[::-1]

            ranked_docs = []
            for i in ranked_indices[:top_k]:
                doc = docs[i].copy()
                doc["similarity_score"] = float(similarities[i])
                ranked_docs.append(doc)

            elapsed = time.time() - start_time
            logger.info(
                f"Ranked {len(docs)} chunks in {elapsed:.3f}s, top similarity: {similarities[ranked_indices[0]]:.3f}"
            )
            return ranked_docs

        except Exception as e:
            logger.warning(f"Similarity ranking failed: {e}, using original order")
            return docs[:top_k]

    def _format_chunks_for_processing(self, docs):
        """Optimized formatting with length limits."""
        MAX_CHUNK_LENGTH = 500

        formatted_chunks = []
        for doc in docs:
            content = doc["document"][:MAX_CHUNK_LENGTH]
            if len(doc["document"]) > MAX_CHUNK_LENGTH:
                content += "..."

            formatted_chunks.append(
                f"Content: {content}\n"
                f"Scores: {doc['score']:.3f} (retrieval), {doc.get('similarity_score', 0):.3f} (similarity)"
            )

        return "\n---\n".join(formatted_chunks)

    def forward(self, question):
        start_time = time.time()
        all_context = []
        queries_used = []
        query_objectives = []
        evidence_summaries = []
        hop_conclusions = []
        self.seen_content.clear()

        logger.info("Planning search queries...")
        plan_start = time.time()
        rewrite_result = self.query_rewriter(question=question, max_hops=self.max_hops)
        logger.info(f"Query planning took {time.time() - plan_start:.2f}s")

        search_queries = (
            rewrite_result.search_queries.split("\n")
            if isinstance(rewrite_result.search_queries, str)
            else rewrite_result.search_queries
        )
        search_queries = [self._clean_text(q) for q in search_queries if q.strip()]
        queries_to_use = search_queries[: self.max_hops]

        rewriter_objectives = (
            rewrite_result.query_objectives.split("\n")
            if isinstance(rewrite_result.query_objectives, str)
            else rewrite_result.query_objectives
        )
        rewriter_objectives = [
            self._clean_text(obj) for obj in rewriter_objectives if obj.strip()
        ]

        current_query = queries_to_use[0] if queries_to_use else question
        remaining_queries = queries_to_use[1:] if len(queries_to_use) > 1 else []
        current_objective = (
            rewriter_objectives[0]
            if rewriter_objectives
            else "Find initial information to answer the question"
        )

        for hop in range(self.max_hops):
            hop_start = time.time()
            logger.info(f"Processing hop {hop + 1}: {current_query}")

            docs = self.retriever.retrieve(current_query, k=10)
            unique_docs = self._deduplicate_docs(docs)

            if not unique_docs:
                logger.info(
                    f"No unique documents found at hop {hop + 1}, stopping early"
                )
                break

            ranked_docs = self._rank_chunks_by_similarity(
                question, unique_docs, top_k=5
            )
            context_text = "\n".join([doc["document"] for doc in ranked_docs])

            ranked_chunks_text = self._format_chunks_for_processing(ranked_docs)

            llm_start = time.time()
            hop_result = self.hop_processor(
                original_question=question,
                current_query=current_query,
                query_objective=current_objective,
                ranked_context=ranked_chunks_text,
                previous_evidence=evidence_summaries,
                remaining_queries=remaining_queries,
                hop_number=hop + 1,
                max_hops=self.max_hops,
            )
            logger.info(f"Hop {hop + 1} LLM call took {time.time() - llm_start:.2f}s")

            all_context.append(context_text)
            queries_used.append(current_query)
            query_objectives.append(current_objective)
            evidence_summaries.append(hop_result.evidence_summary)
            hop_conclusions.append(hop_result.hop_conclusion)

            if (
                hop_result.next_query == "DONE"
                or hop_result.confidence_assessment == "sufficient"
                or hop == self.max_hops - 1
            ):
                logger.info(
                    f"Stopping after hop {hop + 1}: {hop_result.confidence_assessment}"
                )
                break

            current_query = self._clean_text(hop_result.next_query)
            current_objective = self._clean_text(hop_result.next_objective)

            if remaining_queries and current_query in remaining_queries:
                remaining_queries.remove(current_query)

            logger.info(f"Hop {hop + 1} total time: {time.time() - hop_start:.2f}s")

        logger.info("Performing final multi-hop reasoning...")
        final_start = time.time()
        final_context = "\n---\n".join(all_context)
        result = self.reason(
            question=question,
            context=final_context,
            queries_used=queries_used,
            evidence_summaries=evidence_summaries,
        )
        logger.info(f"Final reasoning took {time.time() - final_start:.2f}s")

        total_time = time.time() - start_time
        logger.info(f"Total processing time: {total_time:.2f}s")

        return dspy.Prediction(
            question=question,
            queries_used=queries_used,
            query_objectives=query_objectives,
            evidence_summaries=evidence_summaries,
            hop_conclusions=hop_conclusions,
            rewritten_queries=search_queries,
            reasoning_summary=result.reasoning_summary,
            answer=result.answer,
            confidence=result.confidence,
            num_hops=len(queries_used),
            validation={
                "is_supported": result.is_answer_supported,
                "supporting_evidence": "Built into reasoning",
            },
        )
