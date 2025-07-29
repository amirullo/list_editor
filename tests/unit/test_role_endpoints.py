import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.role_model import RoleType
import uuid
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
import asyncio

client = TestClient(app)
user_id = str(uuid.uuid4())
headers = {
    "Content-Type": "application/json",
    "X-User-ID": user_id
}

def test_create_role_success():
    payload = {"role_type": RoleType.WORKER.value}
    response = client.post("/api/roles", headers=headers, json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == f"Role {RoleType.WORKER.value} assigned successfully"
    assert data["data"]["role_type"] == RoleType.WORKER.value
    assert data["data"]["id"] == user_id

def test_create_role_includes_role_data_in_response():
    payload = {"role_type": RoleType.CLIENT.value}
    response = client.post("/api/roles", headers=headers, json=payload)
    
    assert response.status_code == 200
    data = response.json()["data"]
    
    # Verify that the response includes the created role data
    assert "id" in data
    assert "role_type" in data
    assert data["role_type"] == RoleType.CLIENT.value
    assert data["id"] == user_id

def test_create_role_validates_user_id_dependency():
    """Test that user_id dependency is properly resolved before role creation"""

    test_user_id = str(uuid.uuid4())
    custom_headers = {
        "Content-Type": "application/json",
        "X-User-ID": test_user_id
    }
    
    payload = {"role_type": RoleType.WORKER.value}
    
    with patch('app.api.dependencies.get_user_id', return_value=test_user_id):
        response = client.post("/api/roles", headers=custom_headers, json=payload)
    
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == test_user_id
    assert data["role_type"] == RoleType.WORKER.value

def test_create_role_service_dependency_injection():
    """Test that role_service dependency is properly injected and available"""

    test_user_id = str(uuid.uuid4())
    custom_headers = {
        "Content-Type": "application/json",
        "X-User-ID": test_user_id
    }
    
    # Mock the role service and its create_role method
    mock_role_service = MagicMock()
    mock_role = MagicMock()
    mock_role.role_type.value = RoleType.CLIENT.value
    mock_role_service.create_role.return_value = mock_role
    
    payload = {"role_type": RoleType.CLIENT.value}
    
    with patch('app.api.endpoints.role_endpoints.get_role_service', return_value=mock_role_service):
        response = client.post("/api/roles", headers=custom_headers, json=payload)
    
    # Verify the service was called with correct parameters
    mock_role_service.create_role.assert_called_once_with(test_user_id, RoleType.CLIENT)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == f"Role {RoleType.CLIENT.value} assigned successfully"

def test_create_role_handles_missing_role_type():
    payload = {}  # Missing role_type field
    response = client.post("/api/roles", headers=headers, json=payload)
    
    assert response.status_code == 422, f"Expected status code 422, but got {response.status_code}"
    error_detail = response.json()["detail"]
    assert any("role_type" in str(error).lower() for error in error_detail)