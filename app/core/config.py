import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "List Editor"
    DATABASE_URL: str = "postgresql+psycopg2://dev:pymbep-koxzev-hokdU6@localhost:5432/mydb"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()