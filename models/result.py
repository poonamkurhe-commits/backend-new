from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class AnswerSubmission(BaseModel):
    question_id: str
    answer: str  # Can be option index, text, or code
    is_correct: bool
    time_taken: int  # in seconds

class Result(BaseModel):
    user_id: str
    subject: str
    question_type: str
    answers: List[AnswerSubmission]
    score: float
    total_questions: int
    correct_answers: int
    time_spent: int  # total seconds
    completed_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        collection = "results"