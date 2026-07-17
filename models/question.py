from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum

class QuestionType(str, Enum):
    MCQ = "mcq"
    VIVA = "viva"
    CODING = "coding"

class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class MCQQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: int
    explanation: Optional[str] = None

class VivaQuestion(BaseModel):
    question: str
    answer: str
    hints: List[str] = []

class CodingQuestion(BaseModel):
    title: str
    description: str
    sample_input: str
    sample_output: str
    test_cases: List[dict]
    difficulty: Difficulty

class Question(BaseModel):
    type: QuestionType
    subject: str
    topic: str
    data: dict  # Will store MCQQuestion, VivaQuestion, or CodingQuestion
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    class Config:
        collection = "questions"