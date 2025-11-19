import uuid
import requests
from app.models.project_model import Project # Import Project model
from app.models.project_user_model import ProjectUser # Import ProjectUser model
from app.models.user_model import User # Import User model
from app.core.db import SessionLocal # Import SessionLocal for direct DB access

BASE_URL = "http://localhost:8000/api"

def generate_external_userid():
    return str(uuid.uuid4())

def login_or_create_user(external_user_id: str) -> int:
    headers = {"X-User-ID": external_user_id}
    response = requests.post(f"{BASE_URL}/users/login", headers=headers)
    response.raise_for_status()
    return response.json()["internal_id"]

def create_project(external_user_id: str, project_name: str):
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": external_user_id
    }
    payload = {
        "name": project_name
    }
    response = requests.post(f"{BASE_URL}/projects/", headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def test_create_and_get_project():
    # Arrange
    external_user_id = generate_external_userid()
    internal_user_id = login_or_create_user(external_user_id)
    project_name = "New Maintenance Project"
    place_description = "Main building, 2nd floor"

    headers = {
        "Content-Type": "application/json",
        "X-User-ID": external_user_id
    }
    project_data = {
        "name": project_name,
        "place_description": place_description
    }

    # Act
    create_response = requests.post(f"{BASE_URL}/projects/", headers=headers, json=project_data)
    
    # Assert
    assert create_response.status_code == 201
    created_project_data = create_response.json()["data"]
    project_id = created_project_data["id"]

    # Verify the project was created in the database
    db = SessionLocal()
    try:
        db_project = db.query(Project).filter(Project.id == project_id).first()
        assert db_project is not None
        assert db_project.name == project_name
        assert db_project.place_description == place_description
    finally:
        db.close()

    get_response = requests.get(f"{BASE_URL}/projects/{project_id}", headers=headers)
    assert get_response.status_code == 200
    retrieved_project_data = get_response.json()["data"]
    assert retrieved_project_data["name"] == project_name
    assert retrieved_project_data["place_description"] == place_description
    assert retrieved_project_data["id"] == project_id

def test_add_and_remove_user_from_project():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_internal_id = login_or_create_user(creator_external_id)
    user_to_add_external_id = generate_external_userid()
    user_to_add_internal_id = login_or_create_user(user_to_add_external_id)

    headers = {
        "Content-Type": "application/json",
        "X-User-ID": creator_external_id
    }
    project_data = {
        "name": "Project for User Management"
    }
    create_response = requests.post(f"{BASE_URL}/projects/", headers=headers, json=project_data)
    project_id = create_response.json()["data"]["id"]

    # Act: Add user
    add_user_payload = {"user_external_id": user_to_add_external_id}
    add_response = requests.post(f"{BASE_URL}/projects/{project_id}/users", headers=headers, json=add_user_payload)

    # Assert: Add user
    assert add_response.status_code == 200
    add_response_data = add_response.json()["data"]
    assert any(p["user_external_id"] == user_to_add_external_id for p in add_response_data["project_users"])

    # Verify user was added to the database
    db = SessionLocal()
    try:
        db_user = db.query(User).filter(User.internal_id == user_to_add_internal_id).first()
        assert db_user is not None
        db_project_user = db.query(ProjectUser).filter(
            ProjectUser.project_id == project_id,
            ProjectUser.user_id == user_to_add_internal_id
        ).first()
        assert db_project_user is not None
    finally:
        db.close()

    # Act: Remove user
    remove_user_payload = {"user_external_id": user_to_add_external_id}
    remove_response = requests.delete(f"{BASE_URL}/projects/{project_id}/users", headers=headers, json=remove_user_payload)

    # Assert: Remove user
    assert remove_response.status_code == 200
    remove_response_data = remove_response.json()["data"]
    assert not any(p["user_external_id"] == user_to_add_external_id for p in remove_response_data["project_users"])

    # Verify user was removed from the database
    db = SessionLocal()
    try:
        db_user = db.query(User).filter(User.internal_id == user_to_add_internal_id).first()
        assert db_user is not None
        db_project_user = db.query(ProjectUser).filter(
            ProjectUser.project_id == project_id,
            ProjectUser.user_id == user_to_add_internal_id
        ).first()
        assert db_project_user is None
    finally:
        db.close()

def test_get_all_projects_for_user():
    # Arrange
    external_user_id = generate_external_userid()
    internal_user_id = login_or_create_user(external_user_id)
    headers = {"Content-Type": "application/json", "X-User-ID": external_user_id}
    requests.post(f"{BASE_URL}/projects/", headers=headers, json={"name": "Project Alpha"})
    requests.post(f"{BASE_URL}/projects/", headers=headers, json={"name": "Project Beta"})

    # Act
    response = requests.get(f"{BASE_URL}/projects/", headers=headers)

    # Assert
    assert response.status_code == 200
    data = response.json()["data"]
    assert isinstance(data, list)
    assert len(data) >= 2
    project_names = [p["name"] for p in data]
    assert "Project Alpha" in project_names
    assert "Project Beta" in project_names

def test_update_project():
    # Arrange
    external_user_id = generate_external_userid()
    internal_user_id = login_or_create_user(external_user_id)
    headers = {"Content-Type": "application/json", "X-User-ID": external_user_id}
    original_data = {"name": "Original Name", "place_description": "Original Description"}
    create_response = requests.post(f"{BASE_URL}/projects/", headers=headers, json=original_data)
    project_id = create_response.json()["data"]["id"]

    # Act
    updated_name = "Updated Name"
    updated_data = {"name": updated_name, "place_description": "Updated Description"}
    update_response = requests.put(f"{BASE_URL}/projects/{project_id}", headers=headers, json=updated_data)

    # Assert
    assert update_response.status_code == 200
    assert update_response.json()["data"]["name"] == updated_name

    # Verify the project was updated in the database
    db = SessionLocal()
    try:
        db_project = db.query(Project).filter(Project.id == project_id).first()
        assert db_project is not None
        assert db_project.name == updated_name
        assert db_project.place_description == updated_data["place_description"]
    finally:
        db.close()

def test_delete_project():
    # Arrange
    external_user_id = generate_external_userid()
    internal_user_id = login_or_create_user(external_user_id)
    headers = {"Content-Type": "application/json", "X-User-ID": external_user_id}
    project_data = {"name": "To Be Deleted"}
    create_response = requests.post(f"{BASE_URL}/projects/", headers=headers, json=project_data)
    project_id = create_response.json()["data"]["id"]

    # Act
    delete_response = requests.delete(f"{BASE_URL}/projects/{project_id}", headers=headers)
    
    # Assert
    assert delete_response.status_code == 204

    # Verify the project was deleted from the database
    db = SessionLocal()
    try:
        db_project = db.query(Project).filter(Project.id == project_id).first()
        assert db_project is None
    finally:
        db.close()

    get_response = requests.get(f"{BASE_URL}/projects/{project_id}", headers=headers)
    assert get_response.status_code == 404
