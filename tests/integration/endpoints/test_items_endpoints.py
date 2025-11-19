import uuid
import requests
import pytest
from typing import Generator, Dict, Any, Tuple
from app.models.item_model import Item # Import Item model
from app.core.db import SessionLocal # Import SessionLocal for direct DB access

BASE_URL = "http://localhost:8000/api"

def generate_external_userid():
    return str(uuid.uuid4())

def login_or_create_user(external_user_id: str) -> None:
    headers = {"X-User-ID": external_user_id}
    response = requests.post(f"{BASE_URL}/users/login", headers=headers)
    response.raise_for_status()

def create_project(external_user_id: str, project_name: str) -> Dict[str, Any]:
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": external_user_id
    }
    payload = {"name": project_name}
    response = requests.post(f"{BASE_URL}/projects/", headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def create_list(external_user_id: str, project_id: int, list_name: str) -> Dict[str, Any]:
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": external_user_id
    }
    payload = {
        "list_create": {"name": list_name, "project_id": project_id}
    }
    response = requests.post(f"{BASE_URL}/lists/", headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def assign_global_role(external_user_id: str, role_type: str) -> Dict[str, Any]:
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": external_user_id
    }
    payload = {"role_type": role_type}
    response = requests.post(f"{BASE_URL}/roles/global", headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

@pytest.fixture(scope="function")
def setup_list() -> Generator[Tuple[str, int], None, None]:
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
    yield external_user_id, list_id

def test_create_item_successfully(setup_list: Tuple[str, int]):
    # Arrange
    external_user_id, list_id = setup_list
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

def test_get_items_successfully(setup_list: Tuple[str, int]):
    # Arrange
    external_user_id, list_id = setup_list
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

def test_update_item_successfully(setup_list: Tuple[str, int]):
    # Arrange
    external_user_id, list_id = setup_list
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
        db_item = db.query(Item).filter(Item.id == item_data["id"]).first()
        assert db_item is not None
        assert db_item.name == updated_name
    finally:
        db.close()

def test_delete_item_successfully(setup_list: Tuple[str, int]):
    # Arrange
    external_user_id, list_id = setup_list
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

def test_client_updates_item_price_successfully(setup_list: Tuple[str, int]):
    # Arrange
    external_user_id, list_id = setup_list
    assign_global_role(external_user_id, "client")

    headers = {"Content-Type": "application/json", "X-User-ID": external_user_id}
    item_payload = {"name": "Client Item", "price": 10.0}
    create_response = requests.post(f"{BASE_URL}/lists/{list_id}/items", headers=headers, json=item_payload)
    assert create_response.status_code == 200
    item_id = create_response.json()["data"]["id"]

    # Act
    updated_price = 15.5
    update_payload = {"price": updated_price}
    response = requests.put(f"{BASE_URL}/lists/{list_id}/items/{item_id}", headers=headers, json=update_payload)

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Item updated successfully"
    item_data = response_data["data"]
    assert item_data["price"] == updated_price

    # Verify the item was updated in the database
    db = SessionLocal()
    try:
        db_item = db.query(Item).filter(Item.id == item_data["id"]).first()
        assert db_item is not None
        assert db_item.price == updated_price
    finally:
        db.close()

def test_client_cannot_update_item_quantity(setup_list: Tuple[str, int]):
    # Arrange
    external_user_id, list_id = setup_list
    assign_global_role(external_user_id, "client")

    headers = {"Content-Type": "application/json", "X-User-ID": external_user_id}
    item_payload = {"name": "Client Item", "quantity": 1}
    create_response = requests.post(f"{BASE_URL}/lists/{list_id}/items", headers=headers, json=item_payload)
    assert create_response.status_code == 200
    item_id = create_response.json()["data"]["id"]

    # Act
    updated_quantity = 5
    update_payload = {"quantity": updated_quantity}
    response = requests.put(f"{BASE_URL}/lists/{list_id}/items/{item_id}", headers=headers, json=update_payload)

    # Assert
    assert response.status_code == 403 # Forbidden
    response_data = response.json()
    assert "Clients can only update item prices." in response_data["message"]

    # Verify the item was NOT updated in the database
    db = SessionLocal()
    try:
        db_item = db.query(Item).filter(Item.id == item_id).first()
        assert db_item is not None
        assert db_item.quantity == 1 # Should remain original quantity
    finally:
        db.close()

def test_worker_updates_item_quantity_successfully(setup_list: Tuple[str, int]):
    # Arrange
    external_user_id, list_id = setup_list
    assign_global_role(external_user_id, "worker")

    headers = {"Content-Type": "application/json", "X-User-ID": external_user_id}
    item_payload = {"name": "Worker Item", "quantity": 1}
    create_response = requests.post(f"{BASE_URL}/lists/{list_id}/items", headers=headers, json=item_payload)
    assert create_response.status_code == 200
    item_id = create_response.json()["data"]["id"]

    # Act
    updated_quantity = 5
    update_payload = {"quantity": updated_quantity}
    response = requests.put(f"{BASE_URL}/lists/{list_id}/items/{item_id}", headers=headers, json=update_payload)

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Item updated successfully"
    item_data = response_data["data"]
    assert item_data["quantity"] == updated_quantity

    # Verify the item was updated in the database
    db = SessionLocal()
    try:
        db_item = db.query(Item).filter(Item.id == item_data["id"]).first()
        assert db_item is not None
        assert db_item.quantity == updated_quantity
    finally:
        db.close()

def test_worker_cannot_update_item_price(setup_list: Tuple[str, int]):
    # Arrange
    external_user_id, list_id = setup_list
    assign_global_role(external_user_id, "worker")

    headers = {"Content-Type": "application/json", "X-User-ID": external_user_id}
    item_payload = {"name": "Worker Item", "price": 10.0}
    create_response = requests.post(f"{BASE_URL}/lists/{list_id}/items", headers=headers, json=item_payload)
    assert create_response.status_code == 200
    item_id = create_response.json()["data"]["id"]

    # Act
    updated_price = 20.0
    update_payload = {"price": updated_price}
    response = requests.put(f"{BASE_URL}/lists/{list_id}/items/{item_id}", headers=headers, json=update_payload)

    # Assert
    assert response.status_code == 403 # Forbidden
    response_data = response.json()
    assert "Workers can only update item quantity and status fields (approved, bought, delivered)." in response_data["message"]

    # Verify the item was NOT updated in the database
    db = SessionLocal()
    try:
        db_item = db.query(Item).filter(Item.id == item_id).first()
        assert db_item is not None
        assert db_item.price == 10.0 # Should remain original price
    finally:
        db.close()
