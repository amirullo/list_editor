import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker
from app.main import app
from app.core.db import get_db, Base, engine

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Create database tables once for the test session.
    """
    Base.metadata.create_all(bind=engine)
    yield

@pytest.fixture(scope="function")
def db_session() -> Session:
    """
    Provides a transactional database session for each test function.
    This creates a transaction, yields a session, and commits the transaction after the test.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.commit() # Commit changes after each test
    session.close()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session: Session) -> TestClient:
    """
    Provides a TestClient with the database dependency overridden to use the
    transactional session for each test function.
    """
    app.dependency_overrides[get_db] = lambda: db_session
    
    with TestClient(app) as c:
        yield c
    
    app.dependency_overrides.clear()
