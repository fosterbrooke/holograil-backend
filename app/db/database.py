from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client = AsyncIOMotorClient(settings.MONGO_URL)
db = client[settings.DATABASE_NAME]

async def connect_to_mongo():
    global client
    client = AsyncIOMotorClient(settings.MONGO_URL)

async def close_mongo_connection():
    global client
    if client:
        client.close()