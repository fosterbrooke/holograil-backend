from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URL: str
    DATABASE_NAME: str
    GOOGLE_CLIENT_ID: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    STRIPE_API_KEY: str
    STRIPE_WEBHOOK_SECRET: str

    class Config:
        env_file = ".env"

settings = Settings()