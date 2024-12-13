from datetime import datetime, timedelta
from app.models.user import User
from app.db.database import db
from passlib.context import CryptContext
from fastapi import BackgroundTasks, HTTPException
from bson import ObjectId

from app.utils.user import create_verification_token, send_verification_email

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user(user: User, background_tasks: BackgroundTasks):
    if db is None:
        raise HTTPException(status_code=500, detail="Database is not initialized")
    
    verification_token = create_verification_token()
    user_dict = user.model_dump()
    user_dict.update({
        "password": pwd_context.hash(user.password),
        "is_email_verified": False,
        "email_verification_token": verification_token,
        "email_verification_expires": datetime.now() + timedelta(hours=24)
    })
    
    result = await db["users"].insert_one(user_dict)
    
    # Add email sending task to background tasks
    background_tasks.add_task(
        send_verification_email,
        user.email,
        verification_token
    )
    
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

async def get_user_by_verification_token(token: str):
    user_doc = await db["users"].find_one({"email_verification_token": token})
    if user_doc:
        return User(**user_doc)
    return None

async def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

async def update_user_verification_token(user_id: str, new_token: str):
    result = await db["users"].update_one(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "email_verification_token": new_token,
                "email_verification_expires": datetime.now() + timedelta(hours=24)
            }
        }
    )
    return result.modified_count > 0

async def update_user_verified_status(user_id: str, is_verified: bool):
    result = await db["users"].update_one(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "is_email_verified": is_verified,
                "email_verification_token": None,
                "email_verification_expires": None
            }
        }
    )
    return result.modified_count > 0