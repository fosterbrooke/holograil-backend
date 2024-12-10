from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import user, subscription
from app.db.database import connect_to_mongo, close_mongo_connection

app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

backend_router = APIRouter()

backend_router.include_router(user.router, prefix="/users", tags=["users"])
backend_router.include_router(subscription.router, prefix="/subscriptions", tags=["subscriptions"])

app.include_router(backend_router)