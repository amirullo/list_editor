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

def test_acquire_and_release_lock_successfully():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']

    project_data = create_project(creator_external_id, "Lock Test Project")
    project_id = project_data["data"]["id"]

    list_data = create_list(creator_external_id, project_id, "Lock Test List")
    list_id = list_data["data"]["id"]

    headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}

    # Act - Acquire Lock
    acquire_response = requests.post(f"{BASE_URL}/lists/{list_id}/lock", headers=headers)

    # Assert - Acquire Lock
    assert acquire_response.status_code == 200
    acquire_response_data = acquire_response.json()
    assert acquire_response_data["message"] == "Lock acquired successfully"
    assert acquire_response_data["data"]["list_id"] == list_id
    assert acquire_response_data["data"]["holder_id"] == creator_internal_id

    # Act - Release Lock
    release_response = requests.delete(f"{BASE_URL}/lists/{list_id}/lock", headers=headers)

    # Assert - Release Lock
    assert release_response.status_code == 200
    release_response_data = release_response.json()
    assert release_response_data["message"] == "Lock released successfully"

def test_acquire_lock_already_locked():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']

    other_user_external_id = generate_external_userid()
    other_user_data = login_or_create_user(other_user_external_id)
    other_user_internal_id = other_user_data['id']

    project_data = create_project(creator_external_id, "Lock Test Project 2")
    project_id = project_data["data"]["id"]

    list_data = create_list(creator_external_id, project_id, "Lock Test List 2")
    list_id = list_data["data"]["id"]

    # Add other_user to the project
    add_user_payload = {"user_external_id": other_user_external_id}
    requests.post(f"{BASE_URL}/projects/{project_id}/users", headers={"X-User-ID": creator_external_id}, json=add_user_payload)

    creator_headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}
    other_user_headers = {"Content-Type": "application/json", "X-User-ID": other_user_external_id}

    # Creator acquires the lock first
    acquire_response = requests.post(f"{BASE_URL}/lists/{list_id}/lock", headers=creator_headers)
    assert acquire_response.status_code == 200

    # Act - Other user tries to acquire the same lock
    second_acquire_response = requests.post(f"{BASE_URL}/lists/{list_id}/lock", headers=other_user_headers)

    # Assert
    assert second_acquire_response.status_code == 409 # Conflict
    second_acquire_response_data = second_acquire_response.json()
    assert "List is already locked by another user" in second_acquire_response_data["detail"]

def test_release_lock_not_held_by_user():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']

    other_user_external_id = generate_external_userid()
    other_user_data = login_or_create_user(other_user_external_id)
    other_user_internal_id = other_user_data['id']

    project_data = create_project(creator_external_id, "Lock Test Project 3")
    project_id = project_data["data"]["id"]

    list_data = create_list(creator_external_id, project_id, "Lock Test List 3")
    list_id = list_data["data"]["id"]

    # Add other_user to the project
    add_user_payload = {"user_external_id": other_user_external_id}
    requests.post(f"{BASE_URL}/projects/{project_id}/users", headers={"X-User-ID": creator_external_id}, json=add_user_payload)

    creator_headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}
    other_user_headers = {"Content-Type": "application/json", "X-User-ID": other_user_external_id}

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
    login_or_create_user(creator_external_id)

    headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}
    non_existent_list_id = 999999

    # Act - Try to release a lock for a non-existent list
    release_response = requests.delete(f"{BASE_URL}/lists/{non_existent_list_id}/lock", headers=headers)

    # Assert
    assert release_response.status_code == 404 # Not Found
    release_response_data = release_response.json()
    assert "List not found" in release_response_data["detail"]
