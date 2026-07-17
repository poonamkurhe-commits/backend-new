from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from bson import ObjectId
from datetime import datetime

from database.connection import Database
from models.result import Result
from routes.auth import get_current_user

router = APIRouter(prefix="/results", tags=["results"])

@router.post("/save")
async def save_result(result_data: dict, current_user = Depends(get_current_user)):
    db = Database.get_collection("results")
    
    try:
        # Validate required fields
        required_fields = ['subject', 'question_type', 'answers', 'score', 'total_questions', 'correct_answers', 'time_spent']
        for field in required_fields:
            if field not in result_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}"
                )
        
        # Create result object
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
        
        # Save to database
        await db.insert_one(result_dict)
        
        return {
            "message": "Result saved successfully",
            "score": result.score,
            "total": result.total_questions,
            "percentage": (result.score / result.total_questions) * 100
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error saving result: {str(e)}"
        )

@router.get("/history")
async def get_results(
    current_user = Depends(get_current_user),
    limit: int = 20,
    subject: str = None
):
    db = Database.get_collection("results")
    
    try:
        # Build query
        query = {"user_id": current_user["user_id"]}
        if subject:
            query["subject"] = subject
        
        # Get results sorted by date
        results = await db.find(query).sort("completed_at", -1).to_list(length=limit)
        
        return [
            {
                "id": str(r["_id"]),
                "subject": r["subject"],
                "type": r["question_type"],
                "score": r["score"],
                "total": r["total_questions"],
                "percentage": round((r["score"] / r["total_questions"]) * 100, 1),
                "correct": r["correct_answers"],
                "date": r["completed_at"].isoformat()
            }
            for r in results
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error fetching results: {str(e)}"
        )

@router.get("/stats")
async def get_stats(current_user = Depends(get_current_user)):
    db = Database.get_collection("results")
    
    try:
        # Get all results for user
        results = await db.find({"user_id": current_user["user_id"]}).to_list(length=1000)
        
        if not results:
            return {
                "total_attempts": 0,
                "average_score": 0,
                "subjects": [],
                "best_score": 0
            }
        
        # Calculate statistics
        total_attempts = len(results)
        total_score = sum(r["score"] for r in results)
        total_questions = sum(r["total_questions"] for r in results)
        
        # Group by subject
        subjects = {}
        for r in results:
            if r["subject"] not in subjects:
                subjects[r["subject"]] = {
                    "attempts": 0,
                    "total_score": 0,
                    "total_questions": 0
                }
            subjects[r["subject"]]["attempts"] += 1
            subjects[r["subject"]]["total_score"] += r["score"]
            subjects[r["subject"]]["total_questions"] += r["total_questions"]
        
        # Format subjects data
        subjects_list = [
            {
                "name": name,
                "attempts": data["attempts"],
                "average_score": round((data["total_score"] / data["total_questions"]) * 100, 1) if data["total_questions"] > 0 else 0
            }
            for name, data in subjects.items()
        ]
        
        return {
            "total_attempts": total_attempts,
            "average_score": round((total_score / total_questions) * 100, 1) if total_questions > 0 else 0,
            "subjects": subjects_list,
            "best_score": max([r["score"] for r in results]) if results else 0
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error fetching stats: {str(e)}"
        )