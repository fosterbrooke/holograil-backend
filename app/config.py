from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URL: str
    DATABASE_NAME: str
    GOOGLE_CLIENT_ID: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    STRIPE_API_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    MAILGUN_API_KEY: str
    MAILGUN_DOMAIN: str
    FRONTEND_URL: str

    class Config:
        env_file = ".env"

settings = Settings()