import uuid
import requests
from app.models.item_model import Item # Import Item model
from app.core.db import SessionLocal # Import SessionLocal for direct DB access

BASE_URL = "http://localhost:8000/api"

def generate_external_userid():
    return str(uuid.uuid4())

def login_or_create_user(external_user_id: str):
    headers = {"X-User-ID": external_user_id}
    response = requests.post(f"{BASE_URL}/users/login", headers=headers)
    response.raise_for_status()
    return response.json()

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

def test_create_item_successfully():
    # Arrange
    external_user_id = generate_external_userid()
    login_or_create_user(external_user_id)
    project_data = create_project(external_user_id, "Test Project")
    project_id = project_data["data"]["id"]
    list_data = create_list(external_user_id, project_id, "Test List for Items")
    list_id = list_data["data"]["id"]

    headers = {"Content-Type": "application/json", "X-User-ID": external_user_id}
    item_payload = {
        "name": "Test Item",
        "description": "A new item"
    }
    
    # Act
    response = requests.post(f"{BASE_URL}/lists/{list_id}/items", headers=headers, json=item_payload)

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Item created successfully"
    item_data = response_data["data"]
    assert item_data["name"] == "Test Item"
    assert item_data["description"] == "A new item"
    assert "id" in item_data
    assert item_data["list_id"] == list_id

    # Verify the item was created in the database
    db = SessionLocal()
    try:
        db_item = db.query(Item).filter(Item.id == item_data["id"]).first()
        assert db_item is not None
        assert db_item.name == item_data["name"]
        assert db_item.description == item_data["description"]
        assert db_item.list_id == list_id
    finally:
        db.close()

def test_get_items_successfully():
    # Arrange
    external_user_id = generate_external_userid()
    login_or_create_user(external_user_id)
    project_data = create_project(external_user_id, "Test Project")
    project_id = project_data["data"]["id"]
    list_data = create_list(external_user_id, project_id, "List for Get Items Test")
    list_id = list_data["data"]["id"]

    headers = {"Content-Type": "application/json", "X-User-ID": external_user_id}
    requests.post(f"{BASE_URL}/lists/{list_id}/items", headers=headers, json={"name": "Item 1"})
    requests.post(f"{BASE_URL}/lists/{list_id}/items", headers=headers, json={"name": "Item 2"})

    # Act
    response = requests.get(f"{BASE_URL}/lists/{list_id}/items", headers=headers)

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Items retrieved successfully"
    retrieved_items = response_data["data"]
    assert len(retrieved_items) == 2
    item_names = [item["name"] for item in retrieved_items]
    assert "Item 1" in item_names
    assert "Item 2" in item_names

def test_update_item_successfully():
    # Arrange
    external_user_id = generate_external_userid()
    login_or_create_user(external_user_id)
    project_data = create_project(external_user_id, "Test Project")
    project_id = project_data["data"]["id"]
    list_data = create_list(external_user_id, project_id, "List for Update Item Test")
    list_id = list_data["data"]["id"]

    headers = {"Content-Type": "application/json", "X-User-ID": external_user_id}
    item_payload = {"name": "Original Item Name"}
    create_response = requests.post(f"{BASE_URL}/lists/{list_id}/items", headers=headers, json=item_payload)
    item_id = create_response.json()["data"]["id"]

    # Act
    updated_name = "Updated Item Name"
    update_payload = {"name": updated_name}
    response = requests.put(f"{BASE_URL}/lists/{list_id}/items/{item_id}", headers=headers, json=update_payload)

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Item updated successfully"
    item_data = response_data["data"]
    assert item_data["name"] == updated_name

    # Verify the item was updated in the database
    db = SessionLocal()
    try:
        db_item = db.query(Item).filter(Item.id == item_id).first()
        assert db_item is not None
        assert db_item.name == updated_name
    finally:
        db.close()

def test_delete_item_successfully():
    # Arrange
    external_user_id = generate_external_userid()
    login_or_create_user(external_user_id)
    project_data = create_project(external_user_id, "Test Project")
    project_id = project_data["data"]["id"]
    list_data = create_list(external_user_id, project_id, "List for Delete Item Test")
    list_id = list_data["data"]["id"]

    headers = {"Content-Type": "application/json", "X-User-ID": external_user_id}
    item_payload = {"name": "Item to Delete"}
    create_response = requests.post(f"{BASE_URL}/lists/{list_id}/items", headers=headers, json=item_payload)
    item_id = create_response.json()["data"]["id"]

    # Act
    response = requests.delete(f"{BASE_URL}/lists/{list_id}/items/{item_id}", headers=headers)

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Item deleted successfully"

    # Verify the item was deleted from the database
    db = SessionLocal()
    try:
        db_item = db.query(Item).filter(Item.id == item_id).first()
        assert db_item is None
    finally:
        db.close()
