
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.db import Base  # Assuming Base is the declarative base for your models
from app.services.list_service import ListService
from app.repositories.list_repository import ListRepository
from app.repositories.list_user_repository import ListUserRepository
from app.repositories.user_repository import UserRepository
from app.repositories.item_repository import ItemRepository
from app.services.global_role_service import GlobalRoleService
from app.services.list_role_service import ListRoleService
from app.schemas.list_schema import ListCreate
import uuid


# In-memory SQLite database for testing
# SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
SQLALCHEMY_DATABASE_URL = "sqlite:///./list_editor.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def generate_userid():
    user_id = str(uuid.uuid4())
    return user_id


@pytest.fixture(scope="function")
def test_db() -> Session:
    """
    Fixture to provide a database session for a single test function.
    Creates all tables before the test and drops them afterwards.
    """
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables
        Base.metadata.drop_all(bind=engine)


def test_create_list_service_success_no_items(test_db: Session):
    """
    Test creating a list successfully with no items directly via the service layer.
    """
    # 1. Setup
    user_id = generate_userid()
    
    # Instantiate repositories and services
    list_repo = ListRepository(test_db)
    list_user_repo = ListUserRepository(test_db)
    user_repo = UserRepository(test_db)
    item_repo = ItemRepository(test_db)
    global_role_service = GlobalRoleService(test_db)
    list_role_service = ListRoleService(test_db)
    
    # The service being tested
    list_service = ListService(
        db=test_db,
        list_repository=list_repo,
        list_user_repository=list_user_repo,
        user_repository=user_repo,
        global_role_service=global_role_service,
        list_role_service=list_role_service,
        item_service=item_repo  # Assuming item_service is an ItemRepository instance
    )

    list_create_data = ListCreate(name="My New Service-Side List")

    # 2. Execute
    created_list = list_service.create_list(
        list_create=list_create_data,
        user_id=user_id,
        items=None
    )

    # 3. Assert
    assert created_list is not None
    assert created_list.name == "My New Service-Side List"
    assert created_list.id is not None
    assert created_list.creator_id == user_id
    assert user_id in created_list.user_id_list
    assert len(created_list.user_id_list) == 1

    # Verify in DB
    db_list_user = list_user_repo.get_by_user_and_list(user_id, created_list.id)
    assert db_list_user is not None
    assert db_list_user.user_id == user_id
    assert db_list_user.list_id == created_list.id
