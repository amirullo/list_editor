import uuid
import requests
from typing import Tuple

BASE_URL = "http://localhost:8000/api"

def generate_external_userid():
    return str(uuid.uuid4())

def login_or_create_user(external_user_id: str) -> Tuple[int, str]: # Return internal_id (int) and external_id (str)
    headers = {"X-User-ID": external_user_id}
    response = requests.post(f"{BASE_URL}/users/login", headers=headers)
    response.raise_for_status()
    response_data = response.json()
    return int(response_data["internal_id"]), response_data["external_id"]

def create_project(external_user_id: str, project_name: str): # Use external_user_id
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": external_user_id # Use external_user_id in header
    }
    payload = {
        "name": project_name
    }
    response = requests.post(f"{BASE_URL}/projects/", headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def create_list(external_user_id: str, project_id: int, list_name: str): # Use external_user_id
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": external_user_id # Use external_user_id in header
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

def test_acquire_and_release_lock_successfully():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_internal_id, creator_external_id_returned = login_or_create_user(creator_external_id) # Get both IDs

    project_data = create_project(creator_external_id_returned, "Lock Test Project") # Pass external_user_id
    project_id = project_data["data"]["id"]

    list_data = create_list(creator_external_id_returned, project_id, "Lock Test List") # Pass external_user_id
    list_id = list_data["data"]["id"]

    headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id_returned} # Use external_user_id in header

    # Ensure no lock exists before starting
    requests.delete(f"{BASE_URL}/lists/{list_id}/lock", headers=headers)

    try:
        # Act - Acquire Lock
        acquire_response = requests.post(f"{BASE_URL}/lists/{list_id}/lock", headers=headers)

        # Assert - Acquire Lock
        assert acquire_response.status_code == 200
        acquire_response_data = acquire_response.json()
        assert acquire_response_data["message"] == "Lock acquired successfully"
        assert acquire_response_data["data"]["list_id"] == list_id
        print(f"acquire_response_data['data']['holder_id'] type: {type(acquire_response_data['data']['holder_id'])}, value: {acquire_response_data['data']['holder_id']}")
        print(f"creator_internal_id type: {type(creator_internal_id)}, value: {creator_internal_id}")
        assert acquire_response_data["data"]["holder_id"] == creator_internal_id # Compare with internal_id

    finally:
        # Act - Release Lock
        release_response = requests.delete(f"{BASE_URL}/lists/{list_id}/lock", headers=headers)

        # Assert - Release Lock
        assert release_response.status_code == 200
        release_response_data = release_response.json()
        assert release_response_data["message"] == "Lock released successfully"

def test_acquire_lock_already_locked():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_internal_id, creator_external_id_returned = login_or_create_user(creator_external_id) # Get both IDs

    other_user_external_id = generate_external_userid()
    other_user_internal_id, other_user_external_id_returned = login_or_create_user(other_user_external_id) # Get both IDs

    project_data = create_project(creator_external_id_returned, "Lock Test Project 2") # Pass external_user_id
    project_id = project_data["data"]["id"]

    list_data = create_list(creator_external_id_returned, project_id, "Lock Test List 2") # Pass external_user_id
    list_id = list_data["data"]["id"]

    # Add other_user to the project
    add_user_payload = {"user_external_id": other_user_external_id_returned} # Use external_user_id
    requests.post(f"{BASE_URL}/projects/{project_id}/users", headers={"X-User-ID": creator_external_id_returned}, json=add_user_payload) # Use external_user_id in header

    creator_headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id_returned} # Use external_user_id in header
    other_user_headers = {"Content-Type": "application/json", "X-User-ID": other_user_external_id_returned} # Use external_user_id in header

    # Creator acquires the lock first
    acquire_response = requests.post(f"{BASE_URL}/lists/{list_id}/lock", headers=creator_headers)
    assert acquire_response.status_code == 200

    # Act - Other user tries to acquire the same lock
    second_acquire_response = requests.post(f"{BASE_URL}/lists/{list_id}/lock", headers=other_user_headers)

    # Assert
    assert second_acquire_response.status_code == 409 # Conflict
    second_acquire_response_data = second_acquire_response.json()
    assert "List is already locked by another user" in second_acquire_response_data["message"] # Changed "detail" to "message"

def test_release_lock_not_held_by_user():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_internal_id, creator_external_id_returned = login_or_create_user(creator_external_id) # Get both IDs

    other_user_external_id = generate_external_userid()
    other_user_internal_id, other_user_external_id_returned = login_or_create_user(other_user_external_id) # Get both IDs

    project_data = create_project(creator_external_id_returned, "Lock Test Project 3") # Pass external_user_id
    project_id = project_data["data"]["id"]

    list_data = create_list(creator_external_id_returned, project_id, "Lock Test List 3") # Pass external_user_id
    list_id = list_data["data"]["id"]

    # Add other_user to the project
    add_user_payload = {"user_external_id": other_user_external_id_returned} # Use external_user_id
    requests.post(f"{BASE_URL}/projects/{project_id}/users", headers={"X-User-ID": creator_external_id_returned}, json=add_user_payload) # Use external_user_id in header

    creator_headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id_returned} # Use external_user_id in header
    other_user_headers = {"Content-Type": "application/json", "X-User-ID": other_user_external_id_returned} # Use external_user_id in header

    # Creator acquires the lock
    acquire_response = requests.post(f"{BASE_URL}/lists/{list_id}/lock", headers=creator_headers)
    assert acquire_response.status_code == 200

    # Act - Other user tries to release the lock
    release_response = requests.delete(f"{BASE_URL}/lists/{list_id}/lock", headers=other_user_headers)

    # Assert
    assert release_response.status_code == 403 # Forbidden
    release_response_data = release_response.json()
    assert "Lock not held by current user or not found" in release_response_data["message"] # Changed "detail" to "message"

def test_release_lock_not_found():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_internal_id, creator_external_id_returned = login_or_create_user(creator_external_id) # Get both IDs

    headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id_returned} # Use external_user_id in header
    non_existent_list_id = 999999

    # Act - Try to release a lock for a non-existent list
    release_response = requests.delete(f"{BASE_URL}/lists/{non_existent_list_id}/lock", headers=headers)

    # Assert
    assert release_response.status_code == 404 # Not Found
    release_response_data = release_response.json()
    assert "List not found" in release_response_data["message"] # Changed "detail" to "message"
