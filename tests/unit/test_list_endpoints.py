import uuid
import requests

BASE_URL = "http://localhost:8000/api"

def generate_external_userid():
    return str(uuid.uuid4())

def login_or_create_user(external_user_id: str):
    headers = {"X-User-ID": external_user_id}
    response = requests.post(f"{BASE_URL}/users/login", headers=headers)
    response.raise_for_status()
    return response.json()["data"]

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

def test_create_list_with_valid_data_no_items():
    # Arrange
    global_role_types = ["client", "worker"]
    list_name = "Valid Test List"
    
    for global_role_type in global_role_types:
        # 1. Create user and get IDs
        external_user_id = generate_external_userid()
        user_data = login_or_create_user(external_user_id)
        user_internal_id = user_data['id']

        # 2. Create global role for the user
        create_global_role_response = create_global_role(external_user_id, user_internal_id, global_role_type)
        assert create_global_role_response.status_code == 200

        # 3. Create list
        headers = {
            "Content-Type": "application/json",
            "X-User-ID": external_user_id
        }
        payload = {
            "list_create": {
                "name": list_name
            },
            "items": None
        }
        
        # Act
        response = requests.post(f"{BASE_URL}/lists/", headers=headers, json=payload)
        
        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["message"] == "List created successfully"
        
        list_data = response_data["data"]
        assert list_data["name"] == list_name
        assert "id" in list_data
        assert list_data["creator_id"] == user_internal_id
        assert user_internal_id in list_data["user_id_list"]

def test_add_user_to_list():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']

    user_to_add_external_id = generate_external_userid()
    user_to_add_data = login_or_create_user(user_to_add_external_id)
    user_to_add_internal_id = user_to_add_data['id']

    headers = {
        "Content-Type": "application/json",
        "X-User-ID": creator_external_id
    }
    list_payload = {
        "list_create": {
            "name": "Add User Test List"
        },
        "items": None
    }
    list_response = requests.post(f"{BASE_URL}/lists/", headers=headers, json=list_payload)
    list_id = list_response.json()["data"]["id"]

    # Act
    add_user_payload = {"user_id_to_add": user_to_add_external_id}
    response = requests.post(f"{BASE_URL}/lists/{list_id}/users", headers=headers, json=add_user_payload)

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "User added to list successfully"
    list_data = response_data["data"]
    assert user_to_add_internal_id in list_data["user_id_list"]
