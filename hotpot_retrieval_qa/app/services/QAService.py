import time
import logging
from typing import Optional
import dspy
import os
from dotenv import load_dotenv

from hotpot_retrieval_qa.multihop import QA
from hotpot_retrieval_qa.app.services.RetrieverService import RetrieverService

load_dotenv()
logger = logging.getLogger(__name__)


class QAService:
    _instance = None
    _qa_system = None
    _lm = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the QA system"""
        if self._qa_system is None:

            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise Exception("Set ANTHROPIC_API_KEY environment variable")

            self._lm = dspy.LM(
                model="anthropic/claude-3-7-sonnet-20250219",
                api_key=api_key,
                max_tokens=1500,
            )

            retriever_service = RetrieverService()
            retriever = retriever_service.get_retriever()

            self._qa_system = QA(retriever, max_hops=3)
            logger.info("QA system initialized")

    async def answer_question(self, question: str, max_hops: Optional[int] = None):
        """Process a question and return the answer"""
        with dspy.context(lm=self._lm, async_max_workers=4):
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
