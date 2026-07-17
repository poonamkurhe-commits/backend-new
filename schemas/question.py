from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class QuestionType(str, Enum):
    MCQ = "mcq"
    VIVA = "viva"
    CODING = "coding"

class MCQSubmission(BaseModel):
    question_id: str
    selected_option: int
    time_taken: int

class VivaSubmission(BaseModel):
    question_id: str
    answer: str
    time_taken: int

class CodingSubmission(BaseModel):
    question_id: str
    code: str
    time_taken: int

class QuestionResponse(BaseModel):
    id: str
    type: str
    subject: str
    topic: str
    data: dict