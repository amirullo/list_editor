import uuid
import requests
from app.models.list_model import List # Import List model
from app.core.db import SessionLocal # Import SessionLocal for direct DB access

BASE_URL = "http://localhost:8000/api"

def generate_external_userid():
    return str(uuid.uuid4())

def login_or_create_user(external_user_id: str) -> int:
    headers = {"X-User-ID": external_user_id}
    response = requests.post(f"{BASE_URL}/users/login", headers=headers)
    response.raise_for_status()
    return response.json()["internal_id"]

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

def create_step(external_user_id: str, project_id: int, step_name: str):
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": external_user_id
    }
    payload = {
        "name": step_name,
        "project_id": project_id
    }
    response = requests.post(f"{BASE_URL}/steps/", headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def get_list_for_step(external_user_id: str, step_id: int):
    # Since we don't have a direct endpoint to get list by step_id easily without searching,
    # we might need to rely on the fact that we can get the list if we know its ID.
    # But wait, the test needs the list ID.
    # The step creation doesn't return the list ID in the response (it returns Step).
    # However, we can fetch the step and see if it has the list ID?
    # The Step schema might not have list_id.
    # Let's check Step schema.
    # Actually, we can just fetch all lists for the project and find the one with the step_id.
    # Or we can assume the list name is "List for {step_name}".
    pass 
    
def create_list_via_step(external_user_id: str, project_id: int, step_name: str):
    step_data = create_step(external_user_id, project_id, step_name)
    step_id = step_data["data"]["id"]
    
    # Now find the list. 
    headers = {"X-User-ID": external_user_id}
    response = requests.get(f"{BASE_URL}/lists/project/{project_id}", headers=headers)
    response.raise_for_status()
    lists = response.json()["data"]
    
    # Assuming the last created list is the one, or match by name
    expected_name = f"List for {step_name}"
    for l in lists:
        if l["name"] == expected_name:
            return {"data": l} # Mimic old response structure for minimal change
            
    raise Exception("List not found for step")

def test_create_list_via_step_creation():
    # Arrange
    external_user_id = generate_external_userid()
    internal_user_id = login_or_create_user(external_user_id)
    project_data = create_project(external_user_id, "Test Project")
    project_id = project_data["data"]["id"]
    step_name = "Step for List"
    expected_list_name = f"List for {step_name}"

    # Act
    # Create step, which should trigger list creation
    step_response = create_step(external_user_id, project_id, step_name)
    step_id = step_response["data"]["id"]

    # Assert
    # Verify list exists via API
    headers = {"X-User-ID": external_user_id}
    response = requests.get(f"{BASE_URL}/lists/project/{project_id}", headers=headers)
    assert response.status_code == 200
    lists = response.json()["data"]
    
    found_list = None
    for l in lists:
        if l["name"] == expected_list_name:
            found_list = l
            break
            
    assert found_list is not None
    assert found_list["project_id"] == project_id
    # We can't easily check step_id in list response unless we added it to schema, 
    # but we can check DB.

    # Verify the list was created in the database
    db = SessionLocal()
    try:
        db_list = db.query(List).filter(List.id == found_list["id"]).first()
        assert db_list is not None
        assert db_list.name == expected_list_name
        assert db_list.project_id == project_id
        assert db_list.step_id == step_id
    finally:
        db.close()

def test_get_all_lists_for_project():
    # Arrange
    external_user_id = generate_external_userid()
    internal_user_id = login_or_create_user(external_user_id)
    project_data = create_project(external_user_id, "Test Project for Lists")
    project_id = project_data["data"]["id"]

    headers = {
        "Content-Type": "application/json",
        "X-User-ID": external_user_id
    }
    # Create a couple of steps in the project, which creates lists
    create_step(external_user_id, project_id, "Step 1")
    create_step(external_user_id, project_id, "Step 2")

    # Act
    response = requests.get(f"{BASE_URL}/lists/project/{project_id}", headers=headers)

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Lists for project retrieved successfully"
    assert len(response_data["data"]) == 2

def test_get_list():
    # Arrange
    external_user_id = generate_external_userid()
    internal_user_id = login_or_create_user(external_user_id)
    project_data = create_project(external_user_id, "Test Project")
    project_id = project_data["data"]["id"]
    step_name = "Step for My Test List"
    list_data = create_list_via_step(external_user_id, project_id, step_name)
    list_id = list_data["data"]["id"]
    list_name = list_data["data"]["name"]

    # Act
    headers = {"X-User-ID": external_user_id}
    response = requests.get(f"{BASE_URL}/lists/{list_id}", headers=headers)

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "List retrieved successfully"
    list_data = response_data["data"]
    assert list_data["id"] == list_id
    assert list_data["name"] == list_name
    # destination_address is None by default when created via step
    assert list_data["destination_address"] is None
    assert list_data["project_id"] == project_id

def test_update_list_name_successfully():
    # Arrange
    external_user_id = generate_external_userid()
    internal_user_id = login_or_create_user(external_user_id)
    project_data = create_project(external_user_id, "Test Project")
    project_id = project_data["data"]["id"]

    headers = {"Content-Type": "application/json", "X-User-ID": external_user_id}
    list_data = create_list_via_step(external_user_id, project_id, "Step for Update")
    list_id = list_data["data"]["id"]

    # Act
    updated_name = "Updated Name"
    updated_destination_address = "666 Silver Ave"
    update_payload = {"name": updated_name, "destination_address": updated_destination_address}
    response = requests.put(f"{BASE_URL}/lists/{list_id}", headers=headers, json=update_payload)

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "List updated successfully"
    list_data = response_data["data"]
    assert list_data["name"] == updated_name
    assert list_data["destination_address"] == updated_destination_address

    # Verify the list was updated in the database
    db = SessionLocal()
    try:
        db_list = db.query(List).filter(List.id == list_id).first()
        assert db_list is not None
        assert db_list.name == updated_name
        assert db_list.destination_address == updated_destination_address
    finally:
        db.close()

def test_delete_list_successfully():
    # Arrange
    external_user_id = generate_external_userid()
    internal_user_id = login_or_create_user(external_user_id)
    project_data = create_project(external_user_id, "Test Project")
    project_id = project_data["data"]["id"]

    headers = {"Content-Type": "application/json", "X-User-ID": external_user_id}
    list_data = create_list_via_step(external_user_id, project_id, "Step for Delete")
    list_id = list_data["data"]["id"]

    # Act
    response = requests.delete(f"{BASE_URL}/lists/{list_id}", headers=headers)

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "List deleted successfully"

    # Verify the list was deleted from the database
    db = SessionLocal()
    try:
        db_list = db.query(List).filter(List.id == list_id).first()
        assert db_list is None
    finally:
        db.close()
