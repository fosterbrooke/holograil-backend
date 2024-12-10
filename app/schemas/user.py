from typing import Optional
from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    avatar_url: Optional[str] = None

class UserInDB(UserCreate):
    id: str

class UserSignIn(BaseModel):
    username: str
    password: str