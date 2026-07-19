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

# ✅ PUBLIC API - No Authentication Required
@router.get("/public")
async def get_public_questions(
    subject: Optional[str] = None,
    limit: int = 50
):
    """Public endpoint - No authentication required"""
    db = Database.get_collection("questions")
    
    query = {"is_active": True}
    if subject:
        query["subject"] = subject
    
    print(f"📡 Query: {query}")  # Debug
    
    pipeline = [
        {"$match": query},
        {"$sample": {"size": limit}}
    ]

    questions = await db.aggregate(pipeline).to_list(length=limit)
    
    print(f"📥 Found {len(questions)} questions")  # Debug
    
    return [
        {
            "id": str(q["_id"]),
            "type": q["type"],
            "subject": q["subject"],
            "topic": q["topic"],
            "data": q["data"]
        }
        for q in questions
    ]

# ✅ AUTHENTICATED API
@router.get("/", response_model=List[QuestionResponse])
async def get_questions(
    subject: Optional[str] = None,
    type: Optional[QuestionType] = None,
    limit: int = 10,
    current_user = Depends(get_current_user)
):
    db = Database.get_collection("questions")
    
    query = {"is_active": True}
    if subject:
        query["subject"] = subject
    if type:
        query["type"] = type
    
    questions = await db.find(query).to_list(length=limit * 2)
    random.shuffle(questions)
    questions = questions[:limit]
    
    return [format_question(q) for q in questions]

@router.post("/mcq/submit")
async def submit_mcq(submission: MCQSubmission, current_user = Depends(get_current_user)):
    db = Database.get_collection("questions")
    
    try:
        question = await db.find_one({"_id": ObjectId(submission.question_id)})
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        correct = question["data"]["correct_answer"] == submission.selected_option
        return {
            "correct": correct,
            "correct_answer": question["data"]["correct_answer"],
            "explanation": question["data"].get("explanation", "No explanation available")
        }
    except:
        raise HTTPException(status_code=400, detail="Invalid submission")

@router.post("/viva/submit")
async def submit_viva(submission: VivaSubmission, current_user = Depends(get_current_user)):
    db = Database.get_collection("questions")
    
    try:
        question = await db.find_one({"_id": ObjectId(submission.question_id)})
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        keywords = question["data"].get("keywords", [])
        matched = sum(1 for k in keywords if k.lower() in submission.answer.lower())
        score = matched / len(keywords) if keywords else 0.5
        
        return {
            "score": score,
            "feedback": f"Matched {int(matched)}/{len(keywords)} key concepts",
            "suggested_answer": question["data"].get("answer", "")
        }
    except:
        raise HTTPException(status_code=400, detail="Invalid submission")

@router.post("/coding/submit")
async def submit_coding(submission: CodingSubmission, current_user = Depends(get_current_user)):
    return {
        "passed": True,
        "feedback": "Solution submitted successfully!",
        "execution_time": submission.time_taken
    }