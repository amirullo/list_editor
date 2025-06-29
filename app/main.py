from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn

from app.api import router
from app.core.db import engine, get_db
from app.models.base import Base

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="List Editor API",
    description="API for managing lists with UUID-based access",
    version="1.0.0"
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

    uvicorn.run(app, host="0.0.0.0", port=8000)