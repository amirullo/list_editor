import uuid
import requests

BASE_URL = "http://localhost:8000/api"

def generate_external_userid():
    return str(uuid.uuid4())

def login_or_create_user(external_user_id: str):
    headers = {"X-User-ID": external_user_id}
    response = requests.post(f"{BASE_URL}/users/login", headers=headers)
    response.raise_for_status()
    return response.json()

def create_global_role(external_user_id: str, user_internal_id: int, global_role_type: str):
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": external_user_id
    }
    payload = {
        "user_id": user_internal_id,
        "role": global_role_type
    }
    response = requests.post(f"{BASE_URL}/roles/global", headers=headers, json=payload)
    return response

def test_create_item_successfully():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']
    create_global_role(creator_external_id, creator_internal_id, 'client')

    headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}
    list_payload = {"list_create": {"name": "Test List for Items"}, "items": None}
    list_response = requests.post(f"{BASE_URL}/lists/", headers=headers, json=list_payload)
    list_id = list_response.json()["data"]["id"]

    # Act
    item_payload = {"name": "Test Item", "description": "A new item"}
    response = requests.post(f"{BASE_URL}/lists/{list_id}/items", headers=headers, json=item_payload)

    # Assert - Initial creation
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Item created successfully"
    item_data = response_data["data"]
    assert item_data["name"] == "Test Item"
    assert item_data["description"] == "A new item"
    assert "id" in item_data
    assert item_data["list_id"] == list_id
    
    created_item_id = item_data["id"]

    # Verify item creation with a GET request
    get_response = requests.get(f"{BASE_URL}/lists/{list_id}/items", headers=headers)
    assert get_response.status_code == 200
    get_response_data = get_response.json()
    assert get_response_data["message"] == "Items retrieved successfully"
    
    retrieved_items = get_response_data["data"]
    assert len(retrieved_items) == 1
    retrieved_item = retrieved_items[0]
    
    assert retrieved_item["id"] == created_item_id
    assert retrieved_item["name"] == item_payload["name"]
    assert retrieved_item["description"] == item_payload["description"]
    assert retrieved_item["list_id"] == list_id


def test_create_item_unauthorized():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']
    create_global_role(creator_external_id, creator_internal_id, 'client')

    unauthorized_external_id = generate_external_userid()
    login_or_create_user(unauthorized_external_id)

    headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}
    list_payload = {"list_create": {"name": "Test List for Items"}, "items": None}
    list_response = requests.post(f"{BASE_URL}/lists/", headers=headers, json=list_payload)
    list_id = list_response.json()["data"]["id"]

    # Act
    unauthorized_headers = {"Content-Type": "application/json", "X-User-ID": unauthorized_external_id}
    item_payload = {"name": "Test Item", "description": "A new item"}
    response = requests.post(f"{BASE_URL}/lists/{list_id}/items", headers=unauthorized_headers, json=item_payload)

    # Assert
    assert response.status_code == 403
    response_data = response.json()
    assert response_data["detail"] == "Access denied to this list"

def test_create_item_in_nonexistent_list():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']
    create_global_role(creator_external_id, creator_internal_id, 'client')

    headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}
    non_existent_list_id = 999999

    # Act
    item_payload = {"name": "Test Item", "description": "A new item"}
    response = requests.post(f"{BASE_URL}/lists/{non_existent_list_id}/items", headers=headers, json=item_payload)

    # Assert
    assert response.status_code == 404
    response_data = response.json()
    assert response_data["detail"] == "List not found"

def test_get_items_successfully():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']
    create_global_role(creator_external_id, creator_internal_id, 'client')

    headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}
    list_payload = {"list_create": {"name": "List for Get Items Test"}, "items": None}
    list_response = requests.post(f"{BASE_URL}/lists/", headers=headers, json=list_payload)
    list_id = list_response.json()["data"]["id"]

    # Create multiple items
    item_payload_1 = {"name": "Item 1", "description": "First item"}
    item_payload_2 = {"name": "Item 2", "description": "Second item"}

    requests.post(f"{BASE_URL}/lists/{list_id}/items", headers=headers, json=item_payload_1)
    requests.post(f"{BASE_URL}/lists/{list_id}/items", headers=headers, json=item_payload_2)

    # Act
    response = requests.get(f"{BASE_URL}/lists/{list_id}/items", headers=headers)

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Items retrieved successfully"
    
    retrieved_items = response_data["data"]
    assert len(retrieved_items) == 2
    
    # Check if the items are present and match
    item_names = [item["name"] for item in retrieved_items]
    assert item_payload_1["name"] in item_names
    assert item_payload_2["name"] in item_names

def test_get_items_unauthorized():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']
    create_global_role(creator_external_id, creator_internal_id, 'client')

    unauthorized_external_id = generate_external_userid()
    login_or_create_user(unauthorized_external_id)

    headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}
    list_payload = {"list_create": {"name": "List for Unauthorized Get Items Test"}, "items": None}
    list_response = requests.post(f"{BASE_URL}/lists/", headers=headers, json=list_payload)
    list_id = list_response.json()["data"]["id"]

    # Create an item in the list
    item_payload = {"name": "Unauthorized Item", "description": "Should not be accessible"}
    requests.post(f"{BASE_URL}/lists/{list_id}/items", headers=headers, json=item_payload)

    # Act
    unauthorized_headers = {"Content-Type": "application/json", "X-User-ID": unauthorized_external_id}
    response = requests.get(f"{BASE_URL}/lists/{list_id}/items", headers=unauthorized_headers)

    # Assert
    assert response.status_code == 403
    response_data = response.json()
    assert response_data["detail"] == "Access denied to this list"

def test_get_items_from_nonexistent_list():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']
    create_global_role(creator_external_id, creator_internal_id, 'client')

    headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}
    non_existent_list_id = 999999

    # Act
    response = requests.get(f"{BASE_URL}/lists/{non_existent_list_id}/items", headers=headers)

    # Assert
    assert response.status_code == 404
    response_data = response.json()
    assert response_data["detail"] == "List not found"

def test_update_item_successfully():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']
    create_global_role(creator_external_id, creator_internal_id, 'client')

    headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}
    list_payload = {"list_create": {"name": "List for Update Item Test"}, "items": None}
    list_response = requests.post(f"{BASE_URL}/lists/", headers=headers, json=list_payload)
    list_id = list_response.json()["data"]["id"]

    # Create an item to update
    item_payload = {"name": "Original Item Name", "description": "Original description"}
    create_response = requests.post(f"{BASE_URL}/lists/{list_id}/items", headers=headers, json=item_payload)
    item_id = create_response.json()["data"]["id"]

    # Act
    updated_name = "Updated Item Name"
    updated_description = "Updated description"
    update_payload = {"name": updated_name, "description": updated_description}
    response = requests.put(f"{BASE_URL}/lists/{list_id}/items/{item_id}", headers=headers, json=update_payload)

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Item updated successfully"
    item_data = response_data["data"]
    assert item_data["id"] == item_id
    assert item_data["name"] == updated_name
    assert item_data["description"] == updated_description
    assert item_data["list_id"] == list_id

    # Verify update with a GET request
    get_response = requests.get(f"{BASE_URL}/lists/{list_id}/items", headers=headers)
    assert get_response.status_code == 200
    get_response_data = get_response.json()
    retrieved_items = get_response_data["data"]
    assert len(retrieved_items) == 1
    retrieved_item = retrieved_items[0]
    assert retrieved_item["name"] == updated_name
    assert retrieved_item["description"] == updated_description

def test_update_item_unauthorized():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']
    create_global_role(creator_external_id, creator_internal_id, 'client')

    unauthorized_external_id = generate_external_userid()
    login_or_create_user(unauthorized_external_id)

    headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}
    list_payload = {"list_create": {"name": "List for Unauthorized Update Item Test"}, "items": None}
    list_response = requests.post(f"{BASE_URL}/lists/", headers=headers, json=list_payload)
    list_id = list_response.json()["data"]["id"]

    # Create an item to update
    item_payload = {"name": "Unauthorized Item", "description": "Should not be updated"}
    create_response = requests.post(f"{BASE_URL}/lists/{list_id}/items", headers=headers, json=item_payload)
    item_id = create_response.json()["data"]["id"]

    # Act
    unauthorized_headers = {"Content-Type": "application/json", "X-User-ID": unauthorized_external_id}
    update_payload = {"name": "Attempted Update"}
    response = requests.put(f"{BASE_URL}/lists/{list_id}/items/{item_id}", headers=unauthorized_headers, json=update_payload)

    # Assert
    assert response.status_code == 403
    response_data = response.json()
    assert response_data["detail"] == "Access denied to this list"

def test_update_item_in_nonexistent_list():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']
    create_global_role(creator_external_id, creator_internal_id, 'client')

    headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}
    non_existent_list_id = 999999
    item_id = 1 # Dummy item ID

    # Act
    update_payload = {"name": "Attempted Update"}
    response = requests.put(f"{BASE_URL}/lists/{non_existent_list_id}/items/{item_id}", headers=headers, json=update_payload)

    # Assert
    assert response.status_code == 404
    response_data = response.json()
    assert response_data["detail"] == "List not found"

def test_update_nonexistent_item():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']
    create_global_role(creator_external_id, creator_internal_id, 'client')

    headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}
    list_payload = {"list_create": {"name": "List for Nonexistent Item Update Test"}, "items": None}
    list_response = requests.post(f"{BASE_URL}/lists/", headers=headers, json=list_payload)
    list_id = list_response.json()["data"]["id"]

    non_existent_item_id = 999999

    # Act
    update_payload = {"name": "Attempted Update"}
    response = requests.put(f"{BASE_URL}/lists/{list_id}/items/{non_existent_item_id}", headers=headers, json=update_payload)

    # Assert
    assert response.status_code == 404
    response_data = response.json()
    assert response_data["detail"] == "Item not found"

def test_update_item_price_with_client_role_successfully():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']
    create_global_role_response = create_global_role(creator_external_id, creator_internal_id, 'client')
    assert create_global_role_response.status_code == 200

    headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}
    list_payload = {"list_create": {"name": "List for Price Update Test"}, "items": None}
    list_response = requests.post(f"{BASE_URL}/lists/", headers=headers, json=list_payload)
    list_id = list_response.json()["data"]["id"]

    item_payload = {"name": "Item with Price", "description": "Price test"}
    create_response = requests.post(f"{BASE_URL}/lists/{list_id}/items", headers=headers, json=item_payload)
    item_id = create_response.json()["data"]["id"]

    # Act
    updated_price = 10.99
    update_payload = {"price": updated_price}
    response = requests.put(f"{BASE_URL}/lists/{list_id}/items/{item_id}", headers=headers, json=update_payload)

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Item updated successfully"
    item_data = response_data["data"]
    assert item_data["price"] == updated_price

    # Verify update with a GET request
    get_response = requests.get(f"{BASE_URL}/lists/{list_id}/items", headers=headers)
    assert get_response.status_code == 200
    get_response_data = get_response.json()
    retrieved_items = get_response_data["data"]
    assert len(retrieved_items) == 1
    retrieved_item = retrieved_items[0]
    assert retrieved_item["id"] == item_id
    assert retrieved_item["price"] == updated_price


def test_update_item_price_without_client_role_forbidden():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']
    create_global_role_response = create_global_role(creator_external_id, creator_internal_id, 'worker')
    assert create_global_role_response.status_code == 200

    headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}
    list_payload = {"list_create": {"name": "List for Price Update Forbidden Test"}, "items": None}
    list_response = requests.post(f"{BASE_URL}/lists/", headers=headers, json=list_payload)
    list_id = list_response.json()["data"]["id"]

    item_payload = {"name": "Item with Price", "description": "Price test"}
    create_response = requests.post(f"{BASE_URL}/lists/{list_id}/items", headers=headers, json=item_payload)
    item_id = create_response.json()["data"]["id"]

    # Act
    update_payload = {"price": 10.99}
    response = requests.put(f"{BASE_URL}/lists/{list_id}/items/{item_id}", headers=headers, json=update_payload)

    # Assert
    assert response.status_code == 403
    response_data = response.json()
    assert "Additional global role restrictions: price (requires CLIENT global role)" in response_data["detail"]

def test_update_item_quantity_with_worker_role_successfully():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']
    create_global_role_response = create_global_role(creator_external_id, creator_internal_id, 'worker')
    assert create_global_role_response.status_code == 200

    headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}
    list_payload = {"list_create": {"name": "List for Quantity Update Test"}, "items": None}
    list_response = requests.post(f"{BASE_URL}/lists/", headers=headers, json=list_payload)
    list_id = list_response.json()["data"]["id"]

    item_payload = {"name": "Item with Quantity", "description": "Quantity test"}
    create_response = requests.post(f"{BASE_URL}/lists/{list_id}/items", headers=headers, json=item_payload)
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

    # Verify update with a GET request
    get_response = requests.get(f"{BASE_URL}/lists/{list_id}/items", headers=headers)
    assert get_response.status_code == 200
    get_response_data = get_response.json()
    retrieved_items = get_response_data["data"]
    assert len(retrieved_items) == 1
    retrieved_item = retrieved_items[0]
    assert retrieved_item["id"] == item_id
    assert retrieved_item["quantity"] == updated_quantity


def test_update_item_quantity_without_worker_role_forbidden():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']
    create_global_role_response = create_global_role(creator_external_id, creator_internal_id, 'client')
    assert create_global_role_response.status_code == 200

    headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}
    list_payload = {"list_create": {"name": "List for Quantity Update Forbidden Test"}, "items": None}
    list_response = requests.post(f"{BASE_URL}/lists/", headers=headers, json=list_payload)
    list_id = list_response.json()["data"]["id"]

    item_payload = {"name": "Item with Quantity", "description": "Quantity test"}
    create_response = requests.post(f"{BASE_URL}/lists/{list_id}/items", headers=headers, json=item_payload)
    item_id = create_response.json()["data"]["id"]

    # Act
    update_payload = {"quantity": 5}
    response = requests.put(f"{BASE_URL}/lists/{list_id}/items/{item_id}", headers=headers, json=update_payload)

    # Assert
    assert response.status_code == 403
    response_data = response.json()
    assert "Additional global role restrictions: quantity (requires WORKER global role)" in response_data["detail"]

def test_delete_item_successfully():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']
    create_global_role(creator_external_id, creator_internal_id, 'client')

    headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}
    list_payload = {"list_create": {"name": "List for Delete Item Test"}, "items": None}
    list_response = requests.post(f"{BASE_URL}/lists/", headers=headers, json=list_payload)
    list_id = list_response.json()["data"]["id"]

    # Create an item to delete
    item_payload = {"name": "Item to Delete", "description": "This item will be deleted"}
    create_response = requests.post(f"{BASE_URL}/lists/{list_id}/items", headers=headers, json=item_payload)
    item_id = create_response.json()["data"]["id"]

    # Verify item exists before deletion
    get_response_before = requests.get(f"{BASE_URL}/lists/{list_id}/items", headers=headers)
    assert get_response_before.status_code == 200
    assert len(get_response_before.json()["data"]) == 1

    # Act
    response = requests.delete(f"{BASE_URL}/lists/{list_id}/items/{item_id}", headers=headers)

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Item deleted successfully"

    # Verify item is deleted with a GET request
    get_response_after = requests.get(f"{BASE_URL}/lists/{list_id}/items", headers=headers)
    assert get_response_after.status_code == 200
    assert len(get_response_after.json()["data"]) == 0

def test_delete_item_unauthorized():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']
    create_global_role(creator_external_id, creator_internal_id, 'client')

    unauthorized_external_id = generate_external_userid()
    login_or_create_user(unauthorized_external_id)

    headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}
    list_payload = {"list_create": {"name": "List for Unauthorized Delete Item Test"}, "items": None}
    list_response = requests.post(f"{BASE_URL}/lists/", headers=headers, json=list_payload)
    list_id = list_response.json()["data"]["id"]

    # Create an item to delete
    item_payload = {"name": "Unauthorized Delete Item", "description": "Should not be deleted"}
    create_response = requests.post(f"{BASE_URL}/lists/{list_id}/items", headers=headers, json=item_payload)
    item_id = create_response.json()["data"]["id"]

    # Act
    unauthorized_headers = {"Content-Type": "application/json", "X-User-ID": unauthorized_external_id}
    response = requests.delete(f"{BASE_URL}/lists/{list_id}/items/{item_id}", headers=unauthorized_headers)

    # Assert
    assert response.status_code == 403
    response_data = response.json()
    assert response_data["detail"] == "Access denied to this list"

    # Verify item still exists
    get_response_after = requests.get(f"{BASE_URL}/lists/{list_id}/items", headers=headers)
    assert get_response_after.status_code == 200
    assert len(get_response_after.json()["data"]) == 1

def test_delete_item_in_nonexistent_list():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']
    create_global_role(creator_external_id, creator_internal_id, 'client')

    headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}
    non_existent_list_id = 999999
    item_id = 1 # Dummy item ID

    # Act
    response = requests.delete(f"{BASE_URL}/lists/{non_existent_list_id}/items/{item_id}", headers=headers)

    # Assert
    assert response.status_code == 404
    response_data = response.json()
    assert response_data["detail"] == "List not found"

def test_delete_nonexistent_item():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']
    create_global_role(creator_external_id, creator_internal_id, 'client')

    headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}
    list_payload = {"list_create": {"name": "List for Nonexistent Item Delete Test"}, "items": None}
    list_response = requests.post(f"{BASE_URL}/lists/", headers=headers, json=list_payload)
    list_id = list_response.json()["data"]["id"]

    non_existent_item_id = 999999

    # Act
    response = requests.delete(f"{BASE_URL}/lists/{list_id}/items/{non_existent_item_id}", headers=headers)

    # Assert
    assert response.status_code == 404
    response_data = response.json()
    assert response_data["detail"] == "Item not found"
