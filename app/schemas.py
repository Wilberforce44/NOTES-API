from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional

# ---------- User Schemas ----------
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserPublic(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

# ---------- Token Schemas ----------
class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

# ---------- Note Schemas ----------
class NoteCreate(BaseModel):
    title: str
    content: str

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_archived: Optional[bool] = None

class NotePublic(BaseModel):
    id: int
    title: str
    content: str
    is_archived: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
