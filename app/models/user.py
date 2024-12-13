from pydantic import BaseModel, Field, validator
from typing import Optional
from bson import ObjectId
from datetime import datetime

class User(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    username: str
    email: str
    password: str
    avatar_url: Optional[str] = None
    is_email_verified: bool = False
    email_verification_token: Optional[str] = None
    email_verification_expires: Optional[datetime] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    @validator('id', pre=True, always=True)
    def convert_objectid_to_str(cls, v):
        return str(v) if isinstance(v, ObjectId) else v