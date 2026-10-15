from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.ai_assistant import ask_ai

router = APIRouter(
    prefix="/ai",
    tags=["AI Assistant"],
)


class AIQuestion(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Question for the Mini ERP AI Assistant",
    )


class AIAnswer(BaseModel):
    question: str
    answer: str


@router.post("/ask", response_model=AIAnswer)
def ask_assistant(payload: AIQuestion) -> AIAnswer:
    question = payload.question.strip()

    if not question:
        raise HTTPException(
            status_code=422,
            detail="Please enter a question.",
        )

    try:
        answer = ask_ai(question)

        return AIAnswer(
            question=question,
            answer=answer,
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc