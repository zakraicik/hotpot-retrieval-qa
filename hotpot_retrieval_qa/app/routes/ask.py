from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

from hotpot_retrieval_qa.app.services.QAService import QAService

router = APIRouter()
logger = logging.getLogger(__name__)


class QuestionRequest(BaseModel):
    question: str
    max_hops: Optional[int] = 3


class Evidence(BaseModel):
    content: str
    score: float
    rank: int


class QAResponse(BaseModel):
    question: str
    answer: str
    confidence: str
    reasoning_summary: str
    queries_used: List[str]
    query_objectives: List[str]
    evidence_summaries: List[str]
    hop_conclusions: List[str]
    num_hops: int
    processing_time: float


@router.post("/ask", response_model=QAResponse)
async def ask_question(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        qa_service = QAService()
        result = await qa_service.answer_question(
            question=request.question, max_hops=request.max_hops
        )
        return result

    except Exception as e:
        logger.error(f"Error processing question: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
