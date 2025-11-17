from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.project_model import Project
from app.models.step_model import Step

def test_create_and_get_step(client: TestClient, db_session: Session):
    """
    Test creating a new step and then retrieving it to confirm it was created correctly.
    """
    # 1. First, create a project to associate the step with
    project_data = {"name": "Test Project for Step", "place_description": "Test location"}
    project_response = client.post("/api/projects/", json=project_data)
    assert project_response.status_code == 201
    project_id = project_response.json()["id"]

    # 2. Create a new step
    step_data = {
        "name": "First Step",
        "project_id": project_id
    }
    
    create_response = client.post("/api/steps/", json=step_data)
    
    # Verify the creation response
    assert create_response.status_code == 201
    created_step_data = create_response.json()
    assert "id" in created_step_data
    step_id = created_step_data["id"]
    
    # 3. Read the step from the database directly to confirm it's there
    step_in_db = db_session.query(Step).filter(Step.id == step_id).first()
    assert step_in_db is not None
    assert step_in_db.name == step_data["name"]
    assert step_in_db.project_id == project_id
    
    # 4. Get the step via the API endpoint
    get_response = client.get(f"/api/steps/{step_id}")
    
    # Verify the GET response
    assert get_response.status_code == 200
    retrieved_step_data = get_response.json()
    assert retrieved_step_data["name"] == step_data["name"]
    assert retrieved_step_data["project_id"] == project_id
    assert retrieved_step_data["id"] == step_id

def test_create_step_nonexistent_project(client: TestClient):
    """
    Test that creating a step with a non-existent project_id returns a 404 Not Found error.
    """
    step_data = {
        "name": "Step for Non-existent Project",
        "project_id": 99999  # Assuming this project ID does not exist
    }
    
    response = client.post("/api/steps/", json=step_data)
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"

def test_get_nonexistent_step(client: TestClient):
    """
    Test that retrieving a step that does not exist returns a 404 Not Found error.
    """
    response = client.get("/api/steps/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Step not found"

def test_get_all_steps(client: TestClient, db_session: Session):
    """
    Test retrieving all steps for a specific project.
    """
    # 1. Create a project
    project_data = {"name": "Project with Multiple Steps"}
    project_response = client.post("/api/projects/", json=project_data)
    project_id = project_response.json()["id"]
    
    # 2. Create a couple of steps for this project
    client.post("/api/steps/", json={"name": "Step Alpha", "project_id": project_id})
    client.post("/api/steps/", json={"name": "Step Beta", "project_id": project_id})
    
    # 3. Get all steps (note: this endpoint gets ALL steps, not just for one project)
    response = client.get("/api/steps/")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
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
    # 1. Create a project and a step
    project_response = client.post("/api/projects/", json={"name": "Project for Update Test"})
    project_id = project_response.json()["id"]
    create_response = client.post("/api/steps/", json={"name": "Original Step Name", "project_id": project_id})
    step_id = create_response.json()["id"]
    
    # 2. Update the step
    updated_data = {"name": "Updated Step Name", "project_id": project_id}
    update_response = client.put(f"/api/steps/{step_id}", json=updated_data)
    
    # Verify the update response
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Step Name"
    
    # 3. Verify the change in the database
    updated_step_in_db = db_session.query(Step).filter(Step.id == step_id).first()
    assert updated_step_in_db.name == "Updated Step Name"

def test_update_nonexistent_step(client: TestClient):
    """
    Test that updating a step that does not exist returns a 404 Not Found error.
    """
    response = client.put("/api/steps/99999", json={"name": "Won't work", "project_id": 1})
    assert response.status_code == 404
    assert response.json()["detail"] == "Step not found"

def test_delete_step(client: TestClient, db_session: Session):
    """
    Test deleting an existing step.
    """
    # 1. Create a project and a step
    project_response = client.post("/api/projects/", json={"name": "Project for Delete Test"})
    project_id = project_response.json()["id"]
    create_response = client.post("/api/steps/", json={"name": "Step to Be Deleted", "project_id": project_id})
    step_id = create_response.json()["id"]
    
    # 2. Delete the step
    delete_response = client.delete(f"/api/steps/{step_id}")
    assert delete_response.status_code == 204
    
    # 3. Verify it's gone from the database
    deleted_step = db_session.query(Step).filter(Step.id == step_id).first()
    assert deleted_step is None
    
    # 4. Verify that trying to get it returns 404
    get_response = client.get(f"/api/steps/{step_id}")
    assert get_response.status_code == 404

def test_delete_nonexistent_step(client: TestClient):
    """
    Test that deleting a step that does not exist returns a 404 Not Found error.
    """
    response = client.delete("/api/steps/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Step not found"
