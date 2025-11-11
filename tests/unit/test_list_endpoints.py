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
    create_global_role_response = create_global_role(creator_external_id, creator_internal_id, 'client')
    assert create_global_role_response.status_code == 200

    user_to_add_external_id = generate_external_userid()
    user_to_add_data = login_or_create_user(user_to_add_external_id)
    user_to_add_internal_id = user_to_add_data['id']
    create_global_role_response = create_global_role(user_to_add_external_id, user_to_add_internal_id, 'worker')
    assert create_global_role_response.status_code == 200

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
    add_user_payload = {"user_external_id": user_to_add_external_id}
    response = requests.post(f"{BASE_URL}/lists/{list_id}/users", headers=headers, json=add_user_payload)

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "User added to list successfully"
    list_data = response_data["data"]
    assert user_to_add_internal_id in list_data["user_id_list"]

def test_remove_user_from_list():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']
    create_global_role(creator_external_id, creator_internal_id, 'client')

    user_to_remove_external_id = generate_external_userid()
    user_to_remove_data = login_or_create_user(user_to_remove_external_id)
    user_to_remove_internal_id = user_to_remove_data['id']
    create_global_role(user_to_remove_external_id, user_to_remove_internal_id, 'worker')

    headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}
    list_payload = {"list_create": {"name": "Remove User Test List"}, "items": None}
    list_response = requests.post(f"{BASE_URL}/lists/", headers=headers, json=list_payload)
    list_id = list_response.json()["data"]["id"]

    add_user_payload = {"user_external_id": user_to_remove_external_id}
    requests.post(f"{BASE_URL}/lists/{list_id}/users", headers=headers, json=add_user_payload)

    # Act
    remove_user_payload = {"user_external_id": user_to_remove_external_id}
    response = requests.delete(f"{BASE_URL}/lists/{list_id}/users", headers=headers, json=remove_user_payload)

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "User removed from list successfully"
    list_data = response_data["data"]
    assert user_to_remove_internal_id not in list_data["user_id_list"]

def test_remove_user_from_list_not_found():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']
    create_global_role(creator_external_id, creator_internal_id, 'client')

    user_to_remove_external_id = generate_external_userid()
    user_to_remove_data = login_or_create_user(user_to_remove_external_id)
    user_to_remove_internal_id = user_to_remove_data['id']
    create_global_role(user_to_remove_external_id, user_to_remove_internal_id, 'worker')

    headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}
    list_payload = {"list_create": {"name": "Remove User Test List"}, "items": None}
    list_response = requests.post(f"{BASE_URL}/lists/", headers=headers, json=list_payload)
    list_id = list_response.json()["data"]["id"]

    # Act
    # Attempt to remove a user who was never added to the list
    remove_user_payload = {"user_external_id": user_to_remove_external_id}
    response = requests.delete(f"{BASE_URL}/lists/{list_id}/users", headers=headers, json=remove_user_payload)

    # Assert
    assert response.status_code == 404
    response_data = response.json()
    assert response_data["detail"] == 'User not found in this list'

def test_remove_user_from_list_unauthorized():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']
    create_global_role(creator_external_id, creator_internal_id, 'client')

    user_to_remove_external_id = generate_external_userid()
    user_to_remove_data = login_or_create_user(user_to_remove_external_id)
    user_to_remove_internal_id = user_to_remove_data['id']
    create_global_role(user_to_remove_external_id, user_to_remove_internal_id, 'worker')

    # Create an unauthorized user who is not the creator
    unauthorized_external_id = generate_external_userid()
    unauthorized_user_data = login_or_create_user(unauthorized_external_id)
    unauthorized_internal_id = unauthorized_user_data['id']
    create_global_role(unauthorized_external_id, unauthorized_internal_id, 'client')


    headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}
    list_payload = {"list_create": {"name": "Remove User Test List"}, "items": None}
    list_response = requests.post(f"{BASE_URL}/lists/", headers=headers, json=list_payload)
    list_id = list_response.json()["data"]["id"]

    add_user_payload = {"user_external_id": user_to_remove_external_id}
    requests.post(f"{BASE_URL}/lists/{list_id}/users", headers=headers, json=add_user_payload)

    # Act
    # Attempt to remove a user with an unauthorized user ID
    unauthorized_headers = {"Content-Type": "application/json", "X-User-ID": unauthorized_external_id}
    remove_user_payload = {"user_external_id": user_to_remove_external_id}
    response = requests.delete(f"{BASE_URL}/lists/{list_id}/users", headers=unauthorized_headers, json=remove_user_payload)

    # Assert
    assert response.status_code == 403
    response_data = response.json()
    assert response_data["detail"] == "Only list creator can perform this action"

def test_remove_creator_from_list_unauthorized():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']
    create_global_role(creator_external_id, creator_internal_id, 'client')

    user_to_remove_external_id = generate_external_userid()
    user_to_remove_data = login_or_create_user(user_to_remove_external_id)
    user_to_remove_internal_id = user_to_remove_data['id']
    create_global_role(user_to_remove_external_id, user_to_remove_internal_id, 'worker')

    # Create an unauthorized user who is not the creator
    unauthorized_external_id = generate_external_userid()
    unauthorized_user_data = login_or_create_user(unauthorized_external_id)
    unauthorized_internal_id = unauthorized_user_data['id']
    create_global_role(unauthorized_external_id, unauthorized_internal_id, 'client')


    headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}
    list_payload = {"list_create": {"name": "Remove User Test List"}, "items": None}
    list_response = requests.post(f"{BASE_URL}/lists/", headers=headers, json=list_payload)
    list_id = list_response.json()["data"]["id"]

    add_user_payload = {"user_external_id": user_to_remove_external_id}
    requests.post(f"{BASE_URL}/lists/{list_id}/users", headers=headers, json=add_user_payload)

    # Act
    # Attempt to remove a user with an unauthorized user ID
    unauthorized_headers = {"Content-Type": "application/json", "X-User-ID": unauthorized_external_id}
    remove_user_payload = {"user_external_id": creator_external_id}
    response = requests.delete(f"{BASE_URL}/lists/{list_id}/users", headers=unauthorized_headers, json=remove_user_payload)

    # Assert
    assert response.status_code == 403
    response_data = response.json()
    assert response_data["detail"] == "Only list creator can perform this action"


def test_get_all_lists():
    # Arrange
    global_role_types = ["client", "worker"]
    list_name = "Valid Test List"
    several_external_user_id: list = []
    several_internal_user_id: list = []
    several_list_id: list = []

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
        response = requests.post(f"{BASE_URL}/lists/", headers=headers, json=payload)
        response_data = response.json()
        several_list_id.append(response_data['data']['id'])
        several_internal_user_id.append(user_internal_id)
        several_external_user_id.append(external_user_id)

    headers = {
        "Content-Type": "application/json",
        "X-User-ID": several_external_user_id[0]
    }
    add_user_payload = {"user_external_id": several_external_user_id[1]}
    requests.post(f"{BASE_URL}/lists/{several_list_id[0]}/users",
                             headers=headers,
                             json=add_user_payload)

    headers = {
        "Content-Type": "application/json",
        "X-User-ID": several_external_user_id[1]
    }
    payload = {
    }
    response = requests.get(f"{BASE_URL}/lists/", headers=headers, json=payload)

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Lists retrieved successfully"
    list_data = response_data["data"]
    assert user_internal_id in list_data[0]["user_id_list"]
    assert len(list_data) == 2

def test_get_list():
    # Arrange
    global_role_type = "client"
    list_name = "Valid Test List"
    # 1. Create user and get IDs
    external_user_id = generate_external_userid()
    user_data = login_or_create_user(external_user_id)
    user_internal_id = user_data['id']
    # 2. Create global role for the user
    create_global_role(external_user_id, user_internal_id, global_role_type)

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
    response = requests.post(f"{BASE_URL}/lists/", headers=headers, json=payload)
    response_data = response.json()
    list_id = response_data['data']['id']
    add_user_payload = {}
    response = requests.get(f"{BASE_URL}/lists/{list_id}",
                             headers=headers,
                             json=add_user_payload)

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "List retrieved successfully"
    list_data = response_data["data"]
    assert user_internal_id in list_data["user_id_list"]
    assert user_internal_id == list_data["creator_id"]
    assert list_id == list_data["id"]

def test_update_list_name_successfully():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']
    create_global_role(creator_external_id, creator_internal_id, 'client')

    headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}
    list_payload = {"list_create": {"name": "Original Name"}, "items": None}
    list_response = requests.post(f"{BASE_URL}/lists/", headers=headers, json=list_payload)
    list_id = list_response.json()["data"]["id"]

    # Act
    updated_name = "Updated Name"
    update_payload = {"name": updated_name}
    response = requests.put(f"{BASE_URL}/lists/{list_id}", headers=headers, json=update_payload)

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "List updated successfully"
    list_data = response_data["data"]
    assert list_data["name"] == updated_name

def test_update_list_unauthorized():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']
    create_global_role(creator_external_id, creator_internal_id, 'client')

    unauthorized_external_id = generate_external_userid()
    unauthorized_user_data = login_or_create_user(unauthorized_external_id)
    unauthorized_internal_id = unauthorized_user_data['id']
    create_global_role(unauthorized_external_id, unauthorized_internal_id, 'client')

    headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}
    list_payload = {"list_create": {"name": "Original Name"}, "items": None}
    list_response = requests.post(f"{BASE_URL}/lists/", headers=headers, json=list_payload)
    list_id = list_response.json()["data"]["id"]

    # Act
    unauthorized_headers = {"Content-Type": "application/json", "X-User-ID": unauthorized_external_id}
    update_payload = {"name": "Updated Name"}
    response = requests.put(f"{BASE_URL}/lists/{list_id}", headers=unauthorized_headers, json=update_payload)

    # Assert
    assert response.status_code == 403
    response_data = response.json()
    assert response_data["detail"] == "Access denied to this list"

def test_update_list_not_found():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']
    create_global_role(creator_external_id, creator_internal_id, 'client')

    headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}
    non_existent_list_id = 999999

    # Act
    update_payload = {"name": "Updated Name"}
    response = requests.put(f"{BASE_URL}/lists/{non_existent_list_id}", headers=headers, json=update_payload)

    # Assert
    assert response.status_code == 404
    response_data = response.json()
    assert response_data["detail"] == "List not found"

def test_delete_list_successfully():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']
    create_global_role(creator_external_id, creator_internal_id, 'client')

    headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}
    list_payload = {"list_create": {"name": "List to be deleted"}, "items": None}
    list_response = requests.post(f"{BASE_URL}/lists/", headers=headers, json=list_payload)
    list_id = list_response.json()["data"]["id"]

    # Act
    response = requests.delete(f"{BASE_URL}/lists/{list_id}", headers=headers)

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "List deleted successfully"

    # Verify the list is actually deleted
    get_response = requests.get(f"{BASE_URL}/lists/{list_id}", headers=headers)
    assert get_response.status_code == 404

def test_delete_list_unauthorized():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']
    create_global_role(creator_external_id, creator_internal_id, 'client')

    unauthorized_external_id = generate_external_userid()
    unauthorized_user_data = login_or_create_user(unauthorized_external_id)
    unauthorized_internal_id = unauthorized_user_data['id']
    create_global_role(unauthorized_external_id, unauthorized_internal_id, 'client')

    headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}
    list_payload = {"list_create": {"name": "List to be deleted"}, "items": None}
    list_response = requests.post(f"{BASE_URL}/lists/", headers=headers, json=list_payload)
    list_id = list_response.json()["data"]["id"]

    # Act
    unauthorized_headers = {"Content-Type": "application/json", "X-User-ID": unauthorized_external_id}
    response = requests.delete(f"{BASE_URL}/lists/{list_id}", headers=unauthorized_headers)

    # Assert
    assert response.status_code == 403
    response_data = response.json()
    assert response_data["detail"] == "Only list creator can perform this action"

def test_delete_list_not_found():
    # Arrange
    creator_external_id = generate_external_userid()
    creator_data = login_or_create_user(creator_external_id)
    creator_internal_id = creator_data['id']
    create_global_role(creator_external_id, creator_internal_id, 'client')

    headers = {"Content-Type": "application/json", "X-User-ID": creator_external_id}
    non_existent_list_id = 999999

    # Act
    response = requests.delete(f"{BASE_URL}/lists/{non_existent_list_id}", headers=headers)

    # Assert
    assert response.status_code == 404
    response_data = response.json()
    assert response_data["detail"] == "List not found"
