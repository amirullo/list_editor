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

def add_user_to_list_endpoint(creator_external_id: str, list_id: int, user_external_id_to_add: str):
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": creator_external_id
    }
    payload = {
        "user_external_id": user_external_id_to_add,
        "role": "viewer"  # Assuming 'viewer' role for adding other users
    }
    response = requests.post(f"{BASE_URL}/lists/{list_id}/users", headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def test_acquire_and_release_lock_successfully():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']
    create_global_role(creator_external_id, creator_internal_id, 'client')

    headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}
    list_payload = {"list_create": {"name": "Lock Test List"}, "items": None}

    # Act - Create List
    list_response = requests.post(f"{BASE_URL}/lists/", headers=headers, json=list_payload)
    assert list_response.status_code == 201
    list_id = list_response.json()["data"]["id"]

    # Assert - Verify list was created correctly by fetching it
    get_list_response = requests.get(f"{BASE_URL}/lists/{list_id}", headers=headers)
    assert get_list_response.status_code == 200
    assert get_list_response.json()["data"]["name"] == "Lock Test List"

    # Act - Acquire Lock
    acquire_response = requests.post(f"{BASE_URL}/lists/{list_id}/lock", headers=headers)

    # Assert - Acquire Lock
    assert acquire_response.status_code == 200
    acquire_response_data = acquire_response.json()
    assert acquire_response_data["message"] == "Lock acquired successfully"
    assert acquire_response_data["status"] == "success" # Top-level status
    assert acquire_response_data["data"]["list_id"] == list_id # Lock object is directly in data
    assert acquire_response_data["data"]["holder_id"] == creator_internal_id

    # Act - Release Lock
    release_response = requests.delete(f"{BASE_URL}/lists/{list_id}/lock", headers=headers)

    # Assert - Release Lock
    assert release_response.status_code == 200
    release_response_data = release_response.json()
    assert release_response_data["message"] == "Lock released successfully"
    assert release_response_data["status"] == "success" # Top-level status, data field is None

def test_acquire_lock_already_locked():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']
    create_global_role(creator_external_id, creator_internal_id, 'client')

    other_user_external_id = generate_external_userid()
    other_user_data = login_or_create_user(other_user_external_id)
    other_user_internal_id = other_user_data['id']
    create_global_role(other_user_external_id, other_user_internal_id, 'worker')

    creator_headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}
    other_user_headers = {"Content-Type": "application/json", "X-User-ID": other_user_external_id}

    list_payload = {"list_create": {"name": "Lock Test List"}, "items": None}
    list_response = requests.post(f"{BASE_URL}/lists/", headers=creator_headers, json=list_payload)
    list_id = list_response.json()["data"]["id"]

    # Add other_user to the list
    add_user_to_list_endpoint(creator_external_id, list_id, other_user_external_id)

    # Creator acquires the lock first
    acquire_response = requests.post(f"{BASE_URL}/lists/{list_id}/lock", headers=creator_headers)
    assert acquire_response.status_code == 200

    # Act - Other user tries to acquire the same lock
    second_acquire_response = requests.post(f"{BASE_URL}/lists/{list_id}/lock", headers=other_user_headers)

    # Assert
    assert second_acquire_response.status_code == 409 # Conflict
    second_acquire_response_data = second_acquire_response.json()
    assert "List is already locked by another user" in second_acquire_response_data["detail"] # Updated expected message

def test_release_lock_not_held_by_user():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']
    create_global_role(creator_external_id, creator_internal_id, 'client')

    other_user_external_id = generate_external_userid()
    other_user_data = login_or_create_user(other_user_external_id)
    other_user_internal_id = other_user_data['id']
    create_global_role(other_user_external_id, other_user_internal_id, 'worker')

    creator_headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}
    other_user_headers = {"Content-Type": "application/json", "X-User-ID": other_user_external_id}

    list_payload = {"list_create": {"name": "Lock Test List"}, "items": None}
    list_response = requests.post(f"{BASE_URL}/lists/", headers=creator_headers, json=list_payload)
    list_id = list_response.json()["data"]["id"]

    # Add other_user to the list
    add_user_to_list_endpoint(creator_external_id, list_id, other_user_external_id)

    # Creator acquires the lock
    acquire_response = requests.post(f"{BASE_URL}/lists/{list_id}/lock", headers=creator_headers)
    assert acquire_response.status_code == 200

    # Act - Other user tries to release the lock
    release_response = requests.delete(f"{BASE_URL}/lists/{list_id}/lock", headers=other_user_headers)

    # Assert
    assert release_response.status_code == 403 # Forbidden
    release_response_data = release_response.json()
    assert "Lock not held by current user or not found" in release_response_data["detail"]

def test_release_lock_not_found():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']
    create_global_role(creator_external_id, creator_internal_id, 'client')

    headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}
    non_existent_list_id = 999999

    # Act - Try to release a lock for a non-existent list
    release_response = requests.delete(f"{BASE_URL}/lists/{non_existent_list_id}/lock", headers=headers)

    # Assert
    assert release_response.status_code == 404 # Not Found
    release_response_data = release_response.json()
    assert "List not found" in release_response_data["detail"]
