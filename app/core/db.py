from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .config import settings
from app.models import Base  # This will import all models
from app.models.global_role_model import GlobalRole, GlobalRoleType
from app.models.list_role_model import ListRole, ListRoleType

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_roles(db: Session) -> None:
    """Initialize all role types if they don't exist"""
    # Initialize List Roles
    for role_type in ListRoleType:
        existing_role = db.query(ListRole).filter(ListRole.role_type == role_type).first()
        if not existing_role:
            role = ListRole(
                role_type=role_type,
                description=f"{role_type.value} role for list access"
            )
            db.add(role)
    
    # Initialize Global Roles (if needed)
    for role_type in GlobalRoleType:
        # Global roles are created per user, so we don't pre-populate them
        # But we could add validation here if needed
        pass
    
    db.commit()

# Add this to your existing database initialization
def initialize_database(db: Session) -> None:
    """Initialize database with required data"""
    init_roles(db)
    # Add other initialization as needed