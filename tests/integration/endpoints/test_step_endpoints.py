from app.models.project_model import Project
from app.models.step_model import Step # Import Step model
from app.schemas.project_schema import ProjectCreate # Import ProjectCreate
from app.core.db import SessionLocal # Uncommented SessionLocal import
import uuid
import requests

BASE_URL = "http://localhost:8000/api"

def generate_external_userid():
    return str(uuid.uuid4())

def login_or_create_user(external_user_id: str) -> int:
    headers = {"X-User-ID": external_user_id}
    response = requests.post(f"{BASE_URL}/users/login", headers=headers)
    response.raise_for_status()
    return response.json()["internal_id"]

def test_create_and_get_step(): # Removed client and db_session
    """
    Test creating a new step and then retrieving it to confirm it was created correctly.
    """
    # Arrange
    external_user_id = generate_external_userid()
    internal_user_id = login_or_create_user(external_user_id)
    headers = {"X-User-ID": external_user_id, "Content-Type": "application/json"}

    # 1. First, create a project to associate the step with
    project_data = ProjectCreate(name="Test Project for Step", place_description="Test location")
    project_response = requests.post(f"{BASE_URL}/projects/", headers=headers, json=project_data.model_dump()) # Changed client.post to requests.post
    assert project_response.status_code == 201
    project_id = project_response.json()["data"]["id"]

    # 2. Create a new step
    step_data = {
        "name": "First Step",
        "project_id": project_id
    }
    
    create_response = requests.post(f"{BASE_URL}/steps/", headers=headers, json=step_data) # Changed client.post to requests.post
    
    # Verify the creation response
    assert create_response.status_code == 201
    created_step_data = create_response.json()["data"]
    assert "id" in created_step_data
    step_id = created_step_data["id"]
    
    # Verify the step was created in the database
    db = SessionLocal() # Using SessionLocal for direct DB access
    try:
        db_step = db.query(Step).filter(Step.id == step_id).first()
        assert db_step is not None
        assert db_step.name == step_data["name"]
        assert db_step.project_id == project_id
    finally:
        db.close()

    # 4. Get the step via the API endpoint
    get_response = requests.get(f"{BASE_URL}/steps/{step_id}", headers=headers) # Changed client.get to requests.get
    
    # Verify the GET response
    assert get_response.status_code == 200
    retrieved_step_data = get_response.json()["data"]
    assert retrieved_step_data["name"] == step_data["name"]
    assert retrieved_step_data["project_id"] == project_id
    assert retrieved_step_data["id"] == step_id

def test_create_step_nonexistent_project(): # Removed client
    """
    Test that creating a step with a non-existent project_id returns a 404 Not Found error.
    """
    external_user_id = generate_external_userid()
    internal_user_id = login_or_create_user(external_user_id)
    headers = {"X-User-ID": external_user_id, "Content-Type": "application/json"}

    step_data = {
        "name": "Step for Non-existent Project",
        "project_id": 99999  # Assuming this project ID does not exist
    }
    
    response = requests.post(f"{BASE_URL}/steps/", headers=headers, json=step_data) # Changed client.post to requests.post
    
    assert response.status_code == 404
    assert response.json()["message"] == "Project not found or you don't have access" # Changed "detail" to "message"

def test_get_nonexistent_step(): # Removed client
    """
    Test that retrieving a step that does not exist returns a 404 Not Found error.
    """
    external_user_id = generate_external_userid()
    internal_user_id = login_or_create_user(external_user_id)
    headers = {"X-User-ID": external_user_id, "Content-Type": "application/json"}

    response = requests.get(f"{BASE_URL}/steps/99999", headers=headers) # Changed client.get to requests.get
    assert response.status_code == 404
    assert response.json()["message"] == "Step not found" # Changed "detail" to "message"

def test_get_all_steps(): # Removed client and db_session
    """
    Test retrieving all steps for a specific project.
    """
    # Arrange
    external_user_id = generate_external_userid()
    internal_user_id = login_or_create_user(external_user_id)
    headers = {"X-User-ID": external_user_id, "Content-Type": "application/json"}

    # 1. Create a project
    project_data = ProjectCreate(name="Project with Multiple Steps")
    project_response = requests.post(f"{BASE_URL}/projects/", headers=headers, json=project_data.model_dump()) # Changed client.post to requests.post
    assert project_response.status_code == 201
    project_id = project_response.json()["data"]["id"]
    
    # 2. Create a couple of steps for this project
    requests.post(f"{BASE_URL}/steps/", headers=headers, json={"name": "Step Alpha", "project_id": project_id}) # Changed client.post to requests.post
    requests.post(f"{BASE_URL}/steps/", headers=headers, json={"name": "Step Beta", "project_id": project_id}) # Changed client.post to requests.post
    
    # 3. Get all steps (note: this endpoint gets ALL steps, not just for one project)
    response = requests.get(f"{BASE_URL}/steps/", headers=headers) # Changed client.get to requests.get
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()["data"]
    assert isinstance(data, list)
    
    # Filter for the steps we just created
    project_steps = [s for s in data if s["project_id"] == project_id]
    assert len(project_steps) == 2
    step_names = [s["name"] for s in project_steps]
    assert "Step Alpha" in step_names
    assert "Step Beta" in step_names

def test_update_step(): # Removed client and db_session
    """
    Test updating an existing step.
    """
    # Arrange
    external_user_id = generate_external_userid()
    internal_user_id = login_or_create_user(external_user_id)
    headers = {"X-User-ID": external_user_id, "Content-Type": "application/json"}

    # 1. Create a project and a step
    project_data = ProjectCreate(name="Project for Update Test")
    project_response = requests.post(f"{BASE_URL}/projects/", headers=headers, json=project_data.model_dump()) # Changed client.post to requests.post
    assert project_response.status_code == 201
    project_id = project_response.json()["data"]["id"]
    create_response = requests.post(f"{BASE_URL}/steps/", headers=headers, json={"name": "Original Step Name", "project_id": project_id}) # Changed client.post to requests.post
    assert create_response.status_code == 201
    step_id = create_response.json()["data"]["id"]
    
    # 2. Update the step
    updated_name = "Updated Step Name"
    updated_data = {"name": updated_name, "project_id": project_id}
    update_response = requests.put(f"{BASE_URL}/steps/{step_id}", headers=headers, json=updated_data) # Changed client.put to requests.put
    
    # Verify the update response
    assert update_response.status_code == 200
    assert update_response.json()["data"]["name"] == updated_name

    # 3. Verify the change in the database
    db = SessionLocal() # Using SessionLocal for direct DB access
    try:
        db_step = db.query(Step).filter(Step.id == step_id).first()
        assert db_step is not None
        assert db_step.name == updated_name
    finally:
        db.close()

def test_update_nonexistent_step(): # Removed client
    """
    Test that updating a step that does not exist returns a 404 Not Found error.
    """
    external_user_id = generate_external_userid()
    internal_user_id = login_or_create_user(external_user_id)
    headers = {"X-User-ID": external_user_id, "Content-Type": "application/json"}

    response = requests.put(f"{BASE_URL}/steps/99999", headers=headers, json={"name": "Won't work", "project_id": 1}) # Changed client.put to requests.put
    assert response.status_code == 404
    assert response.json()["message"] == "Step not found" # Changed "detail" to "message"

def test_delete_step(): # Removed client and db_session
    """
    Test deleting an existing step.
    """
    # Arrange
    external_user_id = generate_external_userid()
    internal_user_id = login_or_create_user(external_user_id)
    headers = {"X-User-ID": external_user_id, "Content-Type": "application/json"}

    # 1. Create a project and a step
    project_data = ProjectCreate(name="Project for Delete Test")
    project_response = requests.post(f"{BASE_URL}/projects/", headers=headers, json=project_data.model_dump()) # Changed client.post to requests.post
    assert project_response.status_code == 201
    project_id = project_response.json()["data"]["id"]
    create_response = requests.post(f"{BASE_URL}/steps/", headers=headers, json={"name": "Step to Be Deleted", "project_id": project_id}) # Changed client.post to requests.post
    assert create_response.status_code == 201
    step_id = create_response.json()["data"]["id"]
    
    # 2. Delete the step
    delete_response = requests.delete(f"{BASE_URL}/steps/{step_id}", headers=headers) # Changed client.delete to requests.delete
    assert delete_response.status_code == 200

    # 3. Verify it's gone from the database
    db = SessionLocal() # Using SessionLocal for direct DB access
    try:
        db_step = db.query(Step).filter(Step.id == step_id).first()
        assert db_step is None
    finally:
        db.close()
    
    # 4. Verify that trying to get it returns 404
    get_response = requests.get(f"{BASE_URL}/steps/{step_id}", headers=headers) # Changed client.get to requests.get
    assert get_response.status_code == 404

def test_delete_nonexistent_step(): # Removed client
    """
    Test that deleting a step that does not exist returns a 404 Not Found error.
    """
    external_user_id = generate_external_userid()
    internal_user_id = login_or_create_user(external_user_id)
    headers = {"X-User-ID": external_user_id, "Content-Type": "application/json"}

    response = requests.delete(f"{BASE_URL}/steps/99999", headers=headers) # Changed client.delete to requests.delete
    assert response.status_code == 404
    assert response.json()["message"] == "Step not found" # Changed "detail" to "message"
