import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "List Editor"
    # DATABASE_URL: str = "sqlite:///./list_editor.db"
    DATABASE_URL: str = "postgresql+psycopg2://dev:pymbep-koxzev-hokdU6@localhost:5432/mydb"

    class Config:
        env_file = ".env"

settings = Settings()