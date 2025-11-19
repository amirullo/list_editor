from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.project_model import Project
from app.models.step_model import Step # Import Step model
from app.schemas.project_schema import ProjectCreate # Import ProjectCreate
# from app.core.db import SessionLocal # Removed SessionLocal import
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

def test_create_and_get_step(client: TestClient, db_session: Session):
    """
    Test creating a new step and then retrieving it to confirm it was created correctly.
    """
    # Arrange
    external_user_id = generate_external_userid()
    login_or_create_user(external_user_id)
    headers = {"X-User-ID": external_user_id, "Content-Type": "application/json"}

    # 1. First, create a project to associate the step with
    project_data = ProjectCreate(name="Test Project for Step", place_description="Test location")
    project_response = client.post("/api/projects/", headers=headers, json=project_data.model_dump())
    assert project_response.status_code == 201
    project_id = project_response.json()["data"]["id"]

    # 2. Create a new step
    step_data = {
        "name": "First Step",
        "project_id": project_id
    }
    
    create_response = client.post("/api/steps/", headers=headers, json=step_data)
    
    # Verify the creation response
    assert create_response.status_code == 201
    created_step_data = create_response.json()["data"]
    assert "id" in created_step_data
    step_id = created_step_data["id"]
    
    # Verify the step was created in the database
    db_step = db_session.query(Step).filter(Step.id == step_id).first()
    assert db_step is not None
    assert db_step.name == step_data["name"]
    assert db_step.project_id == project_id

    # 4. Get the step via the API endpoint
    get_response = client.get(f"/api/steps/{step_id}", headers=headers)
    
    # Verify the GET response
    assert get_response.status_code == 200
    retrieved_step_data = get_response.json()["data"]
    assert retrieved_step_data["name"] == step_data["name"]
    assert retrieved_step_data["project_id"] == project_id
    assert retrieved_step_data["id"] == step_id

def test_create_step_nonexistent_project(client: TestClient):
    """
    Test that creating a step with a non-existent project_id returns a 404 Not Found error.
    """
    external_user_id = generate_external_userid()
    login_or_create_user(external_user_id)
    headers = {"X-User-ID": external_user_id, "Content-Type": "application/json"}

    step_data = {
        "name": "Step for Non-existent Project",
        "project_id": 99999  # Assuming this project ID does not exist
    }
    
    response = client.post("/api/steps/", headers=headers, json=step_data)
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"

def test_get_nonexistent_step(client: TestClient):
    """
    Test that retrieving a step that does not exist returns a 404 Not Found error.
    """
    external_user_id = generate_external_userid()
    login_or_create_user(external_user_id)
    headers = {"X-User-ID": external_user_id, "Content-Type": "application/json"}

    response = client.get(f"/api/steps/99999", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Step not found"

def test_get_all_steps(client: TestClient, db_session: Session):
    """
    Test retrieving all steps for a specific project.
    """
    # Arrange
    external_user_id = generate_external_userid()
    login_or_create_user(external_user_id)
    headers = {"X-User-ID": external_user_id, "Content-Type": "application/json"}

    # 1. Create a project
    project_data = ProjectCreate(name="Project with Multiple Steps")
    project_response = client.post("/api/projects/", headers=headers, json=project_data.model_dump())
    assert project_response.status_code == 201
    project_id = project_response.json()["data"]["id"]
    
    # 2. Create a couple of steps for this project
    client.post("/api/steps/", headers=headers, json={"name": "Step Alpha", "project_id": project_id})
    client.post("/api/steps/", headers=headers, json={"name": "Step Beta", "project_id": project_id})
    
    # 3. Get all steps (note: this endpoint gets ALL steps, not just for one project)
    response = client.get("/api/steps/", headers=headers)
    
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

def test_update_step(client: TestClient, db_session: Session):
    """
    Test updating an existing step.
    """
    # Arrange
    external_user_id = generate_external_userid()
    login_or_create_user(external_user_id)
    headers = {"X-User-ID": external_user_id, "Content-Type": "application/json"}

    # 1. Create a project and a step
    project_data = ProjectCreate(name="Project for Update Test")
    project_response = client.post("/api/projects/", headers=headers, json=project_data.model_dump())
    assert project_response.status_code == 201
    project_id = project_response.json()["data"]["id"]
    create_response = client.post("/api/steps/", headers=headers, json={"name": "Original Step Name", "project_id": project_id})
    assert create_response.status_code == 201
    step_id = create_response.json()["data"]["id"]
    
    # 2. Update the step
    updated_name = "Updated Step Name"
    updated_data = {"name": updated_name, "project_id": project_id}
    update_response = client.put(f"/api/steps/{step_id}", headers=headers, json=updated_data)
    
    # Verify the update response
    assert update_response.status_code == 200
    assert update_response.json()["data"]["name"] == updated_name

    # 3. Verify the change in the database
    db_step = db_session.query(Step).filter(Step.id == step_id).first()
    assert db_step is not None
    assert db_step.name == updated_name

def test_update_nonexistent_step(client: TestClient):
    """
    Test that updating a step that does not exist returns a 404 Not Found error.
    """
    external_user_id = generate_external_userid()
    login_or_create_user(external_user_id)
    headers = {"X-User-ID": external_user_id, "Content-Type": "application/json"}

    response = client.put(f"/api/steps/99999", headers=headers, json={"name": "Won't work", "project_id": 1})
    assert response.status_code == 404
    assert response.json()["detail"] == "Step not found"

def test_delete_step(client: TestClient, db_session: Session):
    """
    Test deleting an existing step.
    """
    # Arrange
    external_user_id = generate_external_userid()
    login_or_create_user(external_user_id)
    headers = {"X-User-ID": external_user_id, "Content-Type": "application/json"}

    # 1. Create a project and a step
    project_data = ProjectCreate(name="Project for Delete Test")
    project_response = client.post("/api/projects/", headers=headers, json=project_data.model_dump())
    assert project_response.status_code == 201
    project_id = project_response.json()["data"]["id"]
    create_response = client.post("/api/steps/", headers=headers, json={"name": "Step to Be Deleted", "project_id": project_id})
    assert create_response.status_code == 201
    step_id = create_response.json()["data"]["id"]
    
    # 2. Delete the step
    delete_response = client.delete(f"/api/steps/{step_id}", headers=headers)
    assert delete_response.status_code == 200 # Changed from 204 to 200 due to ResponseModel

    # 3. Verify it's gone from the database
    db_step = db_session.query(Step).filter(Step.id == step_id).first()
    assert db_step is None
    
    # 4. Verify that trying to get it returns 404
    get_response = client.get(f"/api/steps/{step_id}", headers=headers)
    assert get_response.status_code == 404

def test_delete_nonexistent_step(client: TestClient):
    """
    Test that deleting a step that does not exist returns a 404 Not Found error.
    """
    external_user_id = generate_external_userid()
    login_or_create_user(external_user_id)
    headers = {"X-User-ID": external_user_id, "Content-Type": "application/json"}

    response = client.delete(f"/api/steps/99999", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Step not found"
