import time
import logging
from typing import Optional
import dspy

from hotpot_retrieval_qa.multihop import QA
from hotpot_retrieval_qa.app.services.RetrieverService import RetrieverService
from hotpot_retrieval_qa.dspy_setup import setup_dspy

logger = logging.getLogger(__name__)


class QAService:
    _instance = None
    _qa_system = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):

        if self._qa_system is None:
            if not setup_dspy():
                raise Exception("Failed to initialize DSPy")

            retriever_service = RetrieverService()
            retriever = retriever_service.get_retriever()

            self._qa_system = QA(retriever, max_hops=3)
            logger.info("QA system initialized")

    async def answer_question(self, question: str, max_hops: Optional[int] = None):

        if max_hops:
            self._qa_system.max_hops = max_hops

        async_qa_system = dspy.asyncify(self._qa_system)
        start_time = time.time()
        result = await async_qa_system(question)
        processing_time = time.time() - start_time

        return {
            "question": question,
            "answer": result.answer,
            "confidence": result.confidence,
            "reasoning_summary": result.reasoning_summary,
            "queries_used": getattr(result, "queries_used", []),
            "query_objectives": getattr(result, "query_objectives", []),
            "evidence_summaries": getattr(result, "evidence_summaries", []),
            "hop_conclusions": getattr(result, "hop_conclusions", []),
            "num_hops": getattr(result, "num_hops", 0),
            "processing_time": round(processing_time, 2),
        }
