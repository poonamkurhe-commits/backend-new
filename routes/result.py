from fastapi import APIRouter, HTTPException, Depends
from typing import List
from bson import ObjectId

from database.connection import Database
from models.result import Result
from routes.auth import get_current_user

router = APIRouter(prefix="/results", tags=["results"])

@router.post("/save")
async def save_result(result_data: dict, current_user = Depends(get_current_user)):
    db = Database.get_collection("results")
    
    result = Result(
        user_id=current_user["user_id"],
        subject=result_data["subject"],
        question_type=result_data["question_type"],
        answers=result_data["answers"],
        score=result_data["score"],
        total_questions=result_data["total_questions"],
        correct_answers=result_data["correct_answers"],
        time_spent=result_data["time_spent"]
    )
    
    result_dict = result.dict()
    del result_dict['id']  # Remove id field for insertion
    
    await db.insert_one(result_dict)
    return {"message": "Result saved successfully"}

@router.get("/history")
async def get_results(current_user = Depends(get_current_user)):
    db = Database.get_collection("results")
    
    results = await db.find({"user_id": current_user["user_id"]}).to_list(length=50)
    return [
        {
            "id": str(r["_id"]),
            "subject": r["subject"],
            "type": r["question_type"],
            "score": r["score"],
            "total": r["total_questions"],
            "date": r["completed_at"].isoformat()
        }
        for r in results
    ]