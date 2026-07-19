from fastapi import APIRouter, Depends
from typing import List
from database.connection import Database
from routes.auth import get_current_user

router = APIRouter(prefix="/subjects", tags=["subjects"])

@router.get("/")
async def get_subjects(current_user = Depends(get_current_user)):
    """Get all subjects with user's progress"""
    
    db = Database.get_collection("results")
    
    # Get all results for this user
    results = await db.find({"user_id": current_user["user_id"]}).to_list(length=1000)
    
    # Define all subjects with their details
    all_subjects = [
        {"name": "C Programming", "icon": "⚙️", "color": "#4facfe"},
        {"name": "C++", "icon": "🔄", "color": "#f093fb"},
        {"name": "Java", "icon": "☕", "color": "#f5576c"},
        {"name": "Python", "icon": "🐍", "color": "#43e97b"},
        {"name": "HTML/CSS", "icon": "🌐", "color": "#fa709a"},
        {"name": "DBMS", "icon": "🗄️", "color": "#f6d365"},
        {"name": "Operating System", "icon": "🖥️", "color": "#a18cd1"},
        {"name": "Software Engineering", "icon": "📱", "color": "#fbc2eb"}
    ]
    
    # Calculate progress for each subject from actual results
    for subject in all_subjects:
        # Find results for this subject
        subject_results = [r for r in results if r["subject"].lower() == subject["name"].lower()]
        
        if subject_results:
            # Calculate progress
            total_score = sum(r.get("score", 0) for r in subject_results)
            total_questions = sum(r.get("total_questions", 0) for r in subject_results)
            correct_answers = sum(r.get("correct_answers", 0) for r in subject_results)
            
            subject["progress"] = round((total_score / total_questions) * 100) if total_questions > 0 else 0
            subject["attempts"] = len(subject_results)
            subject["correct"] = correct_answers
            subject["totalQuestions"] = total_questions
        else:
            subject["progress"] = 0
            subject["attempts"] = 0
            subject["correct"] = 0
            subject["totalQuestions"] = 0
    
    return all_subjects