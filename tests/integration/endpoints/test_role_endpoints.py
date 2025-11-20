import uuid
import requests
from app.models.global_role_model import GlobalRole, GlobalRoleType
from app.core.db import SessionLocal

BASE_URL = "http://localhost:8000/api"

def generate_external_userid():
    return str(uuid.uuid4())

def login_or_create_user(external_user_id: str) -> int:
    headers = {"X-User-ID": external_user_id}
    response = requests.post(f"{BASE_URL}/users/login", headers=headers)
    response.raise_for_status()
    return response.json()["internal_id"]

# Removed the setup_and_teardown_db fixture to prevent database cleanup.
# All data created by these tests will persist in the database.

def test_create_global_role_success():
    # Arrange
    external_user_id = generate_external_userid()
    user_internal_id = login_or_create_user(external_user_id)
    role_type = GlobalRoleType.CLIENT

    headers = {
        "Content-Type": "application/json",
        "X-User-ID": external_user_id
    }
    payload = {
        "role_type": role_type.value
    }

    # Act
    response = requests.post(f"{BASE_URL}/roles/global", headers=headers, json=payload)

    # Assert
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["message"] == "Global role created/updated successfully"
    assert response_data["data"]["user_id"] == user_internal_id # user_id is int in model, but API returns it as int
    assert response_data["data"]["role_type"] == role_type.value

    # Verify the role was created in the database
    db = SessionLocal()
    try:
        db_role = db.query(GlobalRole).filter(GlobalRole.user_id == user_internal_id).first()
        assert db_role is not None
        assert db_role.user_id == user_internal_id
        assert db_role.role_type == role_type
    finally:
        db.close()

def test_create_global_role_update_existing():
    # Arrange
    external_user_id = generate_external_userid()
    user_internal_id = login_or_create_user(external_user_id)
    initial_role_type = GlobalRoleType.WORKER
    updated_role_type = GlobalRoleType.CLIENT

    headers = {
        "Content-Type": "application/json",
        "X-User-ID": external_user_id
    }

    # Create initial role
    initial_payload = {"role_type": initial_role_type.value}
    response = requests.post(f"{BASE_URL}/roles/global", headers=headers, json=initial_payload)
    assert response.status_code == 201

    # Act - Update the role
    update_payload = {"role_type": updated_role_type.value}
    response = requests.post(f"{BASE_URL}/roles/global", headers=headers, json=update_payload)

    # Assert
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["message"] == "Global role created/updated successfully"
    assert response_data["data"]["user_id"] == user_internal_id
    assert response_data["data"]["role_type"] == updated_role_type.value

    # Verify the role was updated in the database
    db = SessionLocal()
    try:
        db_role = db.query(GlobalRole).filter(GlobalRole.user_id == user_internal_id).first()
        assert db_role is not None
        assert db_role.user_id == user_internal_id
        assert db_role.role_type == updated_role_type
    finally:
        db.close()

def test_get_global_role_success():
    # Arrange
    external_user_id = generate_external_userid()
    user_internal_id = login_or_create_user(external_user_id)
    role_type = GlobalRoleType.WORKER

    headers = {
        "Content-Type": "application/json",
        "X-User-ID": external_user_id
    }
    payload = {
        "role_type": role_type.value
    }
    requests.post(f"{BASE_URL}/roles/global", headers=headers, json=payload)

    # Act
    response = requests.get(f"{BASE_URL}/roles/global/{user_internal_id}", headers=headers)

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Global role retrieved successfully"
    assert response_data["data"]["user_id"] == user_internal_id
    assert response_data["data"]["role_type"] == role_type.value

def test_get_global_role_not_found():
    # Arrange
    external_user_id = generate_external_userid()
    login_or_create_user(external_user_id) # Login to get a valid X-User-ID
    non_existent_user_id = 99999999 # A user ID that should not exist

    headers = {
        "X-User-ID": external_user_id
    }

    # Act
    response = requests.get(f"{BASE_URL}/roles/global/{non_existent_user_id}", headers=headers)

    # Assert
    assert response.status_code == 404
    response_data = response.json()
    assert response_data["detail"] == "Global role not found for this user"

def test_create_global_role_invalid_role_type():
    # Arrange
    external_user_id = generate_external_userid()
    login_or_create_user(external_user_id)

    headers = {
        "Content-Type": "application/json",
        "X-User-ID": external_user_id
    }
    payload = {
        "role_type": "INVALID_ROLE"
    }

    # Act
    response = requests.post(f"{BASE_URL}/roles/global", headers=headers, json=payload)

    # Assert
    assert response.status_code == 422 # Unprocessable Entity for validation errors
    response_data = response.json()
    assert "Input should be 'client' or 'worker'" in response_data["detail"][0]["msg"] # Updated assertion

def test_delete_global_role_success():
    # Arrange
    external_user_id = generate_external_userid()
    user_internal_id = login_or_create_user(external_user_id)
    role_type = GlobalRoleType.CLIENT

    headers = {
        "Content-Type": "application/json",
        "X-User-ID": external_user_id
    }
    payload = {
        "role_type": role_type.value
    }
    # Create a role to be deleted
    requests.post(f"{BASE_URL}/roles/global", headers=headers, json=payload)

    # Act
    response = requests.delete(f"{BASE_URL}/roles/global/{user_internal_id}", headers=headers)

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Global role deleted successfully"
    assert response_data["data"] is None

    # Verify the role was deleted from the database
    db = SessionLocal()
    try:
        db_role = db.query(GlobalRole).filter(GlobalRole.user_id == user_internal_id).first()
        assert db_role is None
    finally:
        db.close()

def test_delete_global_role_not_found():
    # Arrange
    external_user_id = generate_external_userid()
    login_or_create_user(external_user_id) # Login to get a valid X-User-ID
    non_existent_user_id = 99999998 # A user ID that should not exist and won't be created

    headers = {
        "X-User-ID": external_user_id
    }

    # Act
    response = requests.delete(f"{BASE_URL}/roles/global/{non_existent_user_id}", headers=headers)

    # Assert
    assert response.status_code == 404
    response_data = response.json()
    assert response_data["detail"] == "Global role not found for this user"
