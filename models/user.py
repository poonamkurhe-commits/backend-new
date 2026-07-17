from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

class User(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password_hash: Optional[str]= None
    full_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    class Config:
        collection = "users"