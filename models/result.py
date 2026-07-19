from datetime import datetime
from typing import List
from typing import Union
from pydantic import BaseModel, Field


class AnswerSubmission(BaseModel):
    question_id: str
    answer: int          # MCQ असल्यामुळे int पुरेसा आहे
    is_correct: bool
    time_taken: int


class Result(BaseModel):
    user_id: str
    subject: str
    question_type: str
    answers: List[AnswerSubmission]
    score: float
    total_questions: int
    correct_answers: int
    time_spent: int
    completed_at: datetime = Field(default_factory=datetime.utcnow)

Result.model_rebuild()