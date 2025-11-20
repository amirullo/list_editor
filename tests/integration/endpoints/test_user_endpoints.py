import uuid
import requests
from app.models.user_model import User # Import User model
from app.core.db import SessionLocal # Import SessionLocal for direct DB access

BASE_URL = "http://localhost:8000/api"

def generate_external_userid():
    return str(uuid.uuid4())

def test_login_or_create_user_new_user():
    # Arrange
    external_user_id = generate_external_userid()
    headers = {"X-User-ID": external_user_id}

    # Act
    response = requests.post(f"{BASE_URL}/users/login", headers=headers)

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert "external_id" in response_data
    assert response_data["external_id"] == external_user_id
    assert "internal_id" in response_data
    assert isinstance(int(response_data["internal_id"]), int) # internal_id should be an integer string

    # Verify the user was created in the database
    db = SessionLocal()
    try:
        db_user = db.query(User).filter(User.external_id == external_user_id).first()
        assert db_user is not None
        assert str(db_user.external_id) == external_user_id
        assert db_user.internal_id == int(response_data["internal_id"])
    finally:
        db.close()

def test_login_or_create_user_existing_user():
    # Arrange
    external_user_id = generate_external_userid()
    headers = {"X-User-ID": external_user_id}

    # First login to create the user
    first_response = requests.post(f"{BASE_URL}/users/login", headers=headers)
    assert first_response.status_code == 200
    first_internal_id = first_response.json()["internal_id"]

    # Act - Second login with the same external_user_id
    second_response = requests.post(f"{BASE_URL}/users/login", headers=headers)

    # Assert
    assert second_response.status_code == 200
    second_response_data = second_response.json()
    assert second_response_data["external_id"] == external_user_id
    assert second_response_data["internal_id"] == first_internal_id # Internal ID should be the same

    # Verify the user still exists and is the same in the database
    db = SessionLocal()
    try:
        db_user = db.query(User).filter(User.external_id == external_user_id).first()
        assert db_user is not None
        assert str(db_user.external_id) == external_user_id
        assert db_user.internal_id == first_internal_id
    finally:
        db.close()

def test_login_or_create_user_no_external_id_header():
    # Arrange
    headers = {} # No X-User-ID header

    # Act
    response = requests.post(f"{BASE_URL}/users/login", headers=headers)

    # Assert
    assert response.status_code == 422
    # assert "X-User-ID header is required" in response.json()["detail"]
