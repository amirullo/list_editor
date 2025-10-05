import pytest
import uuid
import requests
import asyncio

BASE_URL = "http://localhost:8000"

def generate_userid():
    user_id = str(uuid.uuid4())
    return user_id

def create_global_role(test_user_id, global_role_type):
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": test_user_id
    }
    payload = {
        "user_id": test_user_id,
        "role": global_role_type
    }
    response = requests.post(f"{BASE_URL}/api/roles/global", headers=headers, json=payload)

    return response

def test_create_list_with_valid_data_no_items():

    # Act
    global_role_types = ["client", "worker"]
    list_name = "Valid Test List"
    responses = []
    for global_role_type in global_role_types:
        test_user_id = generate_userid()

        # Check if global role creation was successful
        create_global_role(test_user_id, global_role_type)

        headers = {
            "Content-Type": "application/json",
            "X-User-ID": test_user_id
        }
        payload = {
            "list_create": {
                "name": list_name
            },
            "items": None
        }
        response = requests.post(f"{BASE_URL}/api/lists", headers=headers, json=payload)
        responses.append(response)

    # Assert
    for response in responses:
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == list_name
        assert "id" in data
        assert response.json()["status"] == "success"
        assert response.json()["message"] == "List created successfully"

