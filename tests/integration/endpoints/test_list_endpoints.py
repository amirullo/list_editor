import uuid
import requests
from app.models.list_model import List # Import List model
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

def create_list(external_user_id: str, project_id: int, list_name: str):
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": external_user_id
    }
    payload = {
        "list_create": {
            "name": list_name,
            "project_id": project_id
        }
    }
    response = requests.post(f"{BASE_URL}/lists/", headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def test_create_list_with_valid_data_no_items():
    # Arrange
    external_user_id = generate_external_userid()
    internal_user_id = login_or_create_user(external_user_id)
    project_data = create_project(external_user_id, "Test Project")
    project_id = project_data["data"]["id"]
    list_name = "Valid Test List"
    destination_address = "123 Main St"

    headers = {
        "Content-Type": "application/json",
        "X-User-ID": external_user_id
    }
    payload = {
        "list_create": {
            "name": list_name,
            "destination_address": destination_address,
            "project_id": project_id
        },
        "items": None
    }

    # Act
    response = requests.post(f"{BASE_URL}/lists/", headers=headers, json=payload)

    # Assert
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["message"] == "List created successfully"

    list_data = response_data["data"]
    assert list_data["name"] == list_name
    assert list_data["destination_address"] == destination_address
    assert "id" in list_data
    assert list_data["project_id"] == project_id

    # Verify the list was created in the database
    db = SessionLocal()
    try:
        db_list = db.query(List).filter(List.id == list_data["id"]).first()
        assert db_list is not None
        assert db_list.name == list_name
        assert db_list.destination_address == destination_address
        assert db_list.project_id == project_id
    finally:
        db.close()

def test_get_all_lists_for_project():
    # Arrange
    external_user_id = generate_external_userid()
    internal_user_id = login_or_create_user(external_user_id)
    project_data = create_project(external_user_id, "Test Project for Lists")
    project_id = project_data["data"]["id"]

    headers = {
        "Content-Type": "application/json",
        "X-User-ID": external_user_id
    }
    # Create a couple of lists in the project
    requests.post(f"{BASE_URL}/lists/", headers=headers, json={
        "list_create": {"name": "List 1", "destination_address": "Addr 1", "project_id": project_id},
        "items": None
    })
    requests.post(f"{BASE_URL}/lists/", headers=headers, json={
        "list_create": {"name": "List 2", "destination_address": "Addr 2", "project_id": project_id},
        "items": None
    })

    # Act
    response = requests.get(f"{BASE_URL}/lists/project/{project_id}", headers=headers)

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Lists for project retrieved successfully"
    assert len(response_data["data"]) == 2

def test_get_list():
    # Arrange
    external_user_id = generate_external_userid()
    internal_user_id = login_or_create_user(external_user_id)
    project_data = create_project(external_user_id, "Test Project")
    project_id = project_data["data"]["id"]
    list_name = "My Test List"
    destination_address = "444 Pine St"

    headers = {
        "Content-Type": "application/json",
        "X-User-ID": external_user_id
    }
    payload = {
        "list_create": {
            "name": list_name,
            "destination_address": destination_address,
            "project_id": project_id
        },
        "items": None
    }
    response = requests.post(f"{BASE_URL}/lists/", headers=headers, json=payload)
    list_id = response.json()["data"]["id"]

    # Act
    response = requests.get(f"{BASE_URL}/lists/{list_id}", headers=headers)

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "List retrieved successfully"
    list_data = response_data["data"]
    assert list_data["id"] == list_id
    assert list_data["name"] == list_name
    assert list_data["destination_address"] == destination_address
    assert list_data["project_id"] == project_id

def test_update_list_name_successfully():
    # Arrange
    external_user_id = generate_external_userid()
    internal_user_id = login_or_create_user(external_user_id)
    project_data = create_project(external_user_id, "Test Project")
    project_id = project_data["data"]["id"]

    headers = {"Content-Type": "application/json", "X-User-ID": external_user_id}
    list_payload = {"list_create": {"name": "Original Name", "destination_address": "555 Gold Rd", "project_id": project_id}, "items": None}
    list_response = requests.post(f"{BASE_URL}/lists/", headers=headers, json=list_payload)
    list_id = list_response.json()["data"]["id"]

    # Act
    updated_name = "Updated Name"
    updated_destination_address = "666 Silver Ave"
    update_payload = {"name": updated_name, "destination_address": updated_destination_address}
    response = requests.put(f"{BASE_URL}/lists/{list_id}", headers=headers, json=update_payload)

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "List updated successfully"
    list_data = response_data["data"]
    assert list_data["name"] == updated_name
    assert list_data["destination_address"] == updated_destination_address

    # Verify the list was updated in the database
    db = SessionLocal()
    try:
        db_list = db.query(List).filter(List.id == list_id).first()
        assert db_list is not None
        assert db_list.name == updated_name
        assert db_list.destination_address == updated_destination_address
    finally:
        db.close()

def test_delete_list_successfully():
    # Arrange
    external_user_id = generate_external_userid()
    internal_user_id = login_or_create_user(external_user_id)
    project_data = create_project(external_user_id, "Test Project")
    project_id = project_data["data"]["id"]

    headers = {"Content-Type": "application/json", "X-User-ID": external_user_id}
    list_payload = {"list_create": {"name": "List to be deleted", "destination_address": "111 Tin Ave", "project_id": project_id}, "items": None}
    list_response = requests.post(f"{BASE_URL}/lists/", headers=headers, json=list_payload)
    list_id = list_response.json()["data"]["id"]

    # Act
    response = requests.delete(f"{BASE_URL}/lists/{list_id}", headers=headers)

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "List deleted successfully"

    # Verify the list was deleted from the database
    db = SessionLocal()
    try:
        db_list = db.query(List).filter(List.id == list_id).first()
        assert db_list is None
    finally:
        db.close()
