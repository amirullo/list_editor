import pytest
import uuid
import requests
import asyncio

BASE_URL = "http://localhost:8000"

def generate_userid():
    user_id = str(uuid.uuid4())
    return user_id

def create_global_role(test_user_id):
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": test_user_id
    }
    payload = {
        "user_id": test_user_id,
        "role_type": "client"
    }
    response = requests.post(f"{BASE_URL}/api/roles/global", headers=headers, json=payload)
    return response

def test_create_list_with_valid_data_no_items():
    test_user_id = generate_userid()

    # Check if global role creation was successful
    role_response = create_global_role(test_user_id)
    print(f"")
    print(f"Global role creation response: {role_response.status_code}, {role_response.text}")

    headers = {
        "Content-Type": "application/json",
        "X-User-ID": test_user_id
    }
    payload = {
        "list_create": {
            "name": "Valid Test List"
        },
        "items": None
    }

    print(f"Sending payload: {payload}")
    response = requests.post(f"{BASE_URL}/api/lists", headers=headers, json=payload)
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")

    if response.status_code != 200:
        print(f"Expected status code 200, but got {response.status_code}. Error detail: {response.text}")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["name"] == payload["list_create"]["name"]
    assert "id" in data
    assert response.json()["status"] == "success"
    assert response.json()["message"] == "List created successfully"

def test_get_all_lists_multiple_lists_success():
    test_user_id = generate_userid()
    
    # Create global role first
    role_response = create_global_role(test_user_id)
    assert role_response.status_code == 200
    
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": test_user_id
    }
    
    # Create multiple lists
    list_names = ["First Test List", "Second Test List", "Third Test List"]
    created_list_ids = []
    
    for list_name in list_names:
        payload = {
            "list_create": {
                "name": list_name
            },
            "items": None
        }
        response = requests.post(f"{BASE_URL}/api/lists", headers=headers, json=payload)
        assert response.status_code == 200
        created_list_ids.append(response.json()["data"]["id"])
    
    # Get all lists
    response = requests.get(f"{BASE_URL}/api/lists", headers=headers)

    print(f"")
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Lists retrieved successfully"
    assert len(data["data"]) == 3
    
    # Verify all created lists are returned
    returned_list_names = [list_data["name"] for list_data in data["data"]]
    for list_name in list_names:
        assert list_name in returned_list_names
    
    # Verify all returned lists have required fields
    for list_data in data["data"]:
        assert "id" in list_data
        assert "name" in list_data
        assert list_data["id"] in created_list_ids