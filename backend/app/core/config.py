from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "AI Resume Analyzer"
    ANTHROPIC_API_KEY: str = ""
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    class Config:
        env_file = ".env"

settings = Settings()