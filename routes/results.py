from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import traceback

from database.connection import Database
from models.result import Result
from routes.auth import get_current_user

router = APIRouter(prefix="/results", tags=["results"])


@router.post("/save")
async def save_result(result_data: dict, current_user=Depends(get_current_user)):
    db = Database.get_collection("results")

    try:
        print("\n========== RESULT DATA ==========")
        print(result_data)

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

        inserted = await db.insert_one(result_dict)

        print("✅ Result Saved Successfully")
        print("Inserted ID:", inserted.inserted_id)

        progress = await calculate_progress(
            current_user["user_id"],
            result.subject
        )

        return {
            "success": True,
            "message": "Result saved successfully",
            "id": str(inserted.inserted_id),
            "score": result.score,
            "total": result.total_questions,
            "percentage": round((result.score / result.total_questions) * 100, 1),
            "progress": progress
        }

    except Exception as e:
        print("\n========== SAVE RESULT ERROR ==========")
        traceback.print_exc()

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

# ==========================
# Calculate Progress
# ==========================
async def calculate_progress(user_id: str, subject: str):
    
    db = Database.get_collection("results")

    results = await db.find({
        "user_id": user_id,
        "subject": subject
    }).to_list(length=1000)

    if not results:
        return 0

    total_correct = sum(r["correct_answers"] for r in results)
    total_questions = sum(r["total_questions"] for r in results)

    if total_questions == 0:
        return 0

    progress = round((total_correct / total_questions) * 100)

    return min(progress, 100)

# ==========================
# Dashboard Stats
# ==========================
@router.get("/stats")
async def get_stats(current_user=Depends(get_current_user)):
    db = Database.get_collection("results")

    results = await db.find({
        "user_id": current_user["user_id"]
    }).to_list(length=1000)

    if not results:
        return {
            "total_attempts": 0,
            "average_score": 0,
            "best_score": 0,
            "subjects": []
        }

    total_attempts = len(results)
    total_score = sum(r.get("score", 0) for r in results)
    total_questions = sum(r.get("total_questions", 0) for r in results)
    best_score = max(r.get("score", 0) for r in results)

    average_score = (
        round((total_score / total_questions) * 100, 1)
        if total_questions > 0 else 0
    )

    # Subject wise stats
    subjects = {}
    for r in results:
        subject = r.get("subject", "Unknown")

        if subject not in subjects:
            subjects[subject] = {
                "attempts": 0,
                "score": 0,
                "questions": 0
            }

        subjects[subject]["attempts"] += 1
        subjects[subject]["score"] += r.get("score", 0)
        subjects[subject]["questions"] += r.get("total_questions", 0)

    subject_list = []

    for name, data in subjects.items():
        avg = (
            round((data["score"] / data["questions"]) * 100, 1)
            if data["questions"] > 0 else 0
        )

        subject_list.append({
            "name": name,
            "attempts": data["attempts"],
            "average_score": avg
        })

    return {
        "total_attempts": total_attempts,
        "average_score": average_score,
        "best_score": best_score,
        "subjects": subject_list
    }


# ==========================
# All Subject Progress
# ==========================
@router.get("/progress/all")
async def get_all_progress(current_user=Depends(get_current_user)):
    subjects = [
        "C Programming",
        "C++",
        "Java",
        "Python",
        "HTML/CSS",
        "DBMS",
        "Operating System",
        "Software Engineering"
    ]

    progress = {}

    for subject in subjects:
        progress[subject] = await calculate_progress(
            current_user["user_id"],
            subject
        )

    return progress


# ==========================
# Result History
# ==========================
@router.get("/history")
async def get_history(current_user=Depends(get_current_user)):
    db = Database.get_collection("results")

    results = await db.find({
        "user_id": current_user["user_id"]
    }).sort("completed_at", -1).to_list(length=20)

    history = []

    for r in results:
        history.append({
            "id": str(r["_id"]),
            "subject": r["subject"],
            "score": r["score"],
            "total": r["total_questions"],
            "percentage": round(
                (r["score"] / r["total_questions"]) * 100,
                1
            ),
            "date": r["completed_at"].isoformat()
        })

    return history