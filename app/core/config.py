import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "List Editor"
    DATABASE_URL: str = "sqlite:///./list_editor.db"
    
    class Config:
        env_file = ".env"

settings = Settings()