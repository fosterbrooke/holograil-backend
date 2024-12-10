from datetime import timedelta
from fastapi import APIRouter, HTTPException
from app.schemas.user import UserCreate, UserInDB, UserSignIn
from app.crud.user import create_user, get_user, get_user_by_username, get_user_by_email, verify_password
from google.oauth2 import id_token
from google.auth.transport import requests
from app.config import settings
from app.utils.jwt import create_access_token
from app.utils.license import extract_license_key, generate_license_key
from app.utils.password import hash_password

router = APIRouter()

@router.post("/signup", response_model=UserInDB)
async def signup_user_endpoint(user: UserCreate):
     existing_user = await get_user_by_email(user.email)
     if existing_user:
          raise HTTPException(status_code=400, detail="Email already registered")
     
     user_id = await create_user(user)
     return await get_user(user_id)

@router.post("/signin")
async def signin_user_endpoint(user: UserSignIn):
    existing_user = await get_user_by_username(user.username)
    if not existing_user or not await verify_password(user.password, existing_user.password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    access_token = create_access_token(
        data={"sub": existing_user.username}, expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "user": existing_user.email}

@router.post("/google-signin")
async def google_signin_endpoint(name: str, email: str, picture: str = None):
        # Check if the user exists in the database by email
        user = await get_user_by_email(email)
        if not user:
            # If user doesn't exist, create a new user
            user_data = UserCreate(
                username=email,
                email=email,
                password="",  # No password needed for OAuth2 users
                avatar_url=picture
            )
            user_id = await create_user(user_data)

        # Create an access token for the user
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=timedelta(minutes=30)
        )

        # Return the access token
        return {"access_token": access_token, "user": email}
    
@router.get("/{user_id}", response_model=UserInDB)
async def get_user_endpoint(user_id: str):
    user = await get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/generate-license", response_model=str)
async def generate_license(user: UserCreate, duration: int):
    duration_timedelta = timedelta(days=duration)
    license_key = generate_license_key(user.dict(), duration_timedelta)
    return license_key

@router.post("/extract-license", response_model=dict)
async def extract_license(token: str):
    user_info, expire_date = extract_license_key(token)
    return {"user_info": user_info, "expire_date": expire_date.isoformat()}