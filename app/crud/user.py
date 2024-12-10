from app.models.user import User
from app.db.database import db
from passlib.context import CryptContext
from fastapi import HTTPException
from bson import ObjectId

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user(user: User):
    if db is None:
        raise HTTPException(status_code=500, detail="Database is not initialized")
    user.password = pwd_context.hash(user.password)
    result = await db["users"].insert_one(user.dict(by_alias=True))
    return result.inserted_id

async def get_user(user_id: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Database is not initialized")
    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    return User(**user) if user else None

async def get_user_by_username(username: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Database is not initialized")
    user = await db["users"].find_one({"username": username})
    return User(**user) if user else None

async def get_user_by_email(email: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Database is not initialized")
    user = await db["users"].find_one({"email": email})
    return User(**user) if user else None

async def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)