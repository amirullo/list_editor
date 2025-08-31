
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
from contextlib import asynccontextmanager

from app.api.endpoints import router
from app.core.config import settings
from app.utils.logger import logger
from app.core.db import engine, get_db, initialize_database
from app.models.base import Base

# Import all models explicitly to ensure they're registered
from app.models.list_model import List
from app.models.item_model import Item
# from app.models.role_model import Role
from app.models.lock_model import Lock
# from app.models.user_model import User
from app.models.global_role_model import GlobalRole
from app.models.list_role_model import ListRole
# Import any other models you have

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Application is starting up")
    db = next(get_db())
    try:
        initialize_database(db)
    finally:
        db.close()
    yield
    # Shutdown
    logger.info("Application is shutting down")

# Initialize FastAPI app
app = FastAPI(
    title="List Editor API",
    description="API for managing lists with UUID-based access",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to List Editor API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    # logger.info("Starting the application")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
