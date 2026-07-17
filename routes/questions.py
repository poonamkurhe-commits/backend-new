from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from bson import ObjectId
import random

from database.connection import Database
from models.question import Question, QuestionType
from schemas.question import QuestionResponse, MCQSubmission, VivaSubmission, CodingSubmission
from routes.auth import get_current_user

router = APIRouter(prefix="/questions", tags=["questions"])

def format_question(question: dict) -> QuestionResponse:
    return QuestionResponse(
        id=str(question["_id"]),
        type=question["type"],
        subject=question["subject"],
        topic=question["topic"],
        data=question["data"]
    )

@router.get("/", response_model=List[QuestionResponse])
async def get_questions(
    subject: Optional[str] = None,
    topic: Optional[str] = None,
    type: Optional[QuestionType] = None,
    limit: int = 10,
    shuffle: bool = True,
    current_user = Depends(get_current_user)
):
    db = Database.get_collection("questions")
    
    # Build query
    query = {"is_active": True}
    if subject:
        query["subject"] = subject
    if topic:
        query["topic"] = topic
    if type:
        query["type"] = type
    
    # Get questions
    questions = await db.find(query).to_list(length=limit * 2)  # Get extra for shuffling
    
    # Shuffle if requested
    if shuffle:
        random.shuffle(questions)
    
    # Limit results
    questions = questions[:limit]
    
    return [format_question(q) for q in questions]

@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(question_id: str, current_user = Depends(get_current_user)):
    db = Database.get_collection("questions")
    
    try:
        if not ObjectId.is_valid(question_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid question ID format"
            )
            
        question = await db.find_one({"_id": ObjectId(question_id), "is_active": True})
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        return format_question(question)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error fetching question: {str(e)}"
        )

@router.post("/mcq/submit")
async def submit_mcq(submission: MCQSubmission, current_user = Depends(get_current_user)):
    db = Database.get_collection("questions")
    
    try:
        if not ObjectId.is_valid(submission.question_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid question ID"
            )
            
        question = await db.find_one({"_id": ObjectId(submission.question_id)})
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        if question["type"] != "mcq":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This question is not an MCQ type"
            )
        
        correct = question["data"]["correct_answer"] == submission.selected_option
        return {
            "correct": correct,
            "correct_answer": question["data"]["correct_answer"],
            "explanation": question["data"].get("explanation", "No explanation available")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error submitting answer: {str(e)}"
        )

@router.post("/viva/submit")
async def submit_viva(submission: VivaSubmission, current_user = Depends(get_current_user)):
    db = Database.get_collection("questions")
    
    try:
        if not ObjectId.is_valid(submission.question_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid question ID"
            )
            
        question = await db.find_one({"_id": ObjectId(submission.question_id)})
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        if question["type"] != "viva":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This question is not a Viva type"
            )
        
        # Simple keyword matching for demonstration
        keywords = question["data"].get("keywords", [])
        if keywords:
            matched = sum(1 for k in keywords if k.lower() in submission.answer.lower())
            score = matched / len(keywords)
        else:
            score = 0.5  # Default score if no keywords
        
        return {
            "score": score,
            "feedback": f"Matched {int(matched)}/{len(keywords)} key concepts" if keywords else "Answer submitted successfully",
            "suggested_answer": question["data"].get("answer", "No suggested answer available")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error submitting answer: {str(e)}"
        )

@router.post("/coding/submit")
async def submit_coding(submission: CodingSubmission, current_user = Depends(get_current_user)):
    # This would integrate with a code execution service
    # For demonstration, we'll return a mock response
    return {
        "passed": True,
        "feedback": "Solution submitted successfully!",
        "execution_time": submission.time_taken,
        "message": "Your code has been received for evaluation"
    }