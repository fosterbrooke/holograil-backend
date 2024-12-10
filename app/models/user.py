from pydantic import BaseModel, Field, validator
from typing import Optional
from bson import ObjectId

class User(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    username: str
    email: str
    password: str
    avatar_url: Optional[str] = None

    @validator('id', pre=True, always=True)
    def convert_objectid_to_str(cls, v):
        return str(v) if isinstance(v, ObjectId) else v