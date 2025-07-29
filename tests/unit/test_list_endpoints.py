import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.role_model import RoleType
import uuid
from unittest.mock import patch
from fastapi import HTTPException
import asyncio

client = TestClient(app)
user_id = str(uuid.uuid4())
headers = {
    "Content-Type": "application/json",
    "X-User-ID": user_id
}

def assign_client_role(headers):
    """Assign client role to the test client."""
    payload = {"role_type": RoleType.CLIENT.value}
    client.post("/api/roles", headers=headers, json=payload)

assign_client_role(headers)

def test_create_list_with_no_items():
    assign_client_role(headers)
    payload = {
        "list_create": {
            "name": "Empty List"
        }
    }
    response = client.post("/api/lists", headers=headers, json=payload)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["name"] == payload["list_create"]["name"]
    assert "items" not in data or len(data["items"]) == 0


def test_create_list_with_multiple_items():

    payload = {
        "list_create": {
            "name": "My List with Items"
        },
        "items": [
            {"name": "Item 1", "description": "First item"},
            {"name": "Item 2", "description": "Second item"},
            {"name": "Item 3", "description": "Third item"}
        ]
    }
    response = client.post("/api/lists", headers=headers, json=payload)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["name"] == payload["list_create"]["name"]
    assert len(data["items"]) == 3
    assert data["items"][0]["name"] == "Item 1"
    assert data["items"][1]["name"] == "Item 2"
    assert data["items"][2]["name"] == "Item 3"




def test_create_list_with_user_id():

    test_user_id = str(uuid.uuid4())
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": test_user_id
    }
    assign_client_role(headers)

    payload = {
        "list_create": {
            "name": "Test List"
        }
    }

    with patch('app.api.endpoints.list_endpoints.ensure_client_role', return_value=test_user_id):
        response = client.post("/api/lists", headers=headers, json=payload)

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["message"] == "List created successfully"
    assert "id" in response.json()["data"]
    assert response.json()["data"]["name"] == "Test List"


def test_create_list_unauthorized():
    unauthorized_user_id = str(uuid.uuid4())
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": unauthorized_user_id
    }
    payload = {
        "list_create": {
            "name": "Unauthorized List"
        }
    }
    with patch('app.api.endpoints.list_endpoints.ensure_client_role',
               side_effect=HTTPException(status_code=403, detail="Unauthorized")):
        response = client.post("/api/lists", headers=headers, json=payload)

    assert response.status_code == 403
    assert response.json()["detail"] == "This action requires client role"


def test_get_lists():
    response = client.get("/api/lists")
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)


# def test_get_list_by_id():
#     # First, create a list to ensure there is one to retrieve
#     payload = {
#         "list_create": {  # Wrap the payload in 'list_create'
#             "name": "Test List"
#         }
#     }
#     create_response = client.post("/api/lists", headers=headers, json=payload)
#     list_id = create_response.json()["data"]["id"]
#
#     # Now, retrieve the list by ID
#     response = client.get(f"/api/lists/{list_id}", headers=headers)
#     assert response.status_code == 200
#     data = response.json()["data"]
#     assert data["id"] == list_id

