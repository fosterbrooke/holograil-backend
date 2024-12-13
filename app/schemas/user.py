from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserInDB(UserCreate):
    id: str
    is_email_verified: bool
    email_verification_token: Optional[str]
    email_verification_expires: Optional[datetime]
    avatar_url: Optional[str]
    created_at: datetime
    updated_at: datetime

class UserSignIn(BaseModel):
    email: str
    password: str