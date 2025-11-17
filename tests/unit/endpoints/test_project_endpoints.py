from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.project_model import Project

def test_create_and_get_project(client: TestClient, db_session: Session):
    """
    Test creating a new project and then retrieving it to confirm it was created correctly.
    """
    # 1. Create a new project
    project_data = {
        "name": "New Maintenance Project",
        "place_description": "Main building, 2nd floor"
    }
    
    create_response = client.post("/api/projects/", json=project_data)
    
    # Verify the creation response
    assert create_response.status_code == 201
    created_project_data = create_response.json()
    assert "id" in created_project_data
    project_id = created_project_data["id"]
    
    # 2. Read the project from the database directly to confirm it's there
    project_in_db = db_session.query(Project).filter(Project.id == project_id).first()
    assert project_in_db is not None
    assert project_in_db.name == project_data["name"]
    assert project_in_db.place_description == project_data["place_description"]
    
    # 3. Get the project via the API endpoint
    get_response = client.get(f"/api/projects/{project_id}")
    
    # Verify the GET response
    assert get_response.status_code == 200
    retrieved_project_data = get_response.json()
    assert retrieved_project_data["name"] == project_data["name"]
    assert retrieved_project_data["place_description"] == project_data["place_description"]
    assert retrieved_project_data["id"] == project_id

def test_create_project_missing_name(client: TestClient):
    """
    Test that creating a project with a missing 'name' field returns a 422 Unprocessable Entity error.
    """
    project_data = {
        "place_description": "This should fail"
    }
    
    response = client.post("/api/projects/", json=project_data)
    
    assert response.status_code == 422

def test_get_nonexistent_project(client: TestClient):
    """
    Test that retrieving a project that does not exist returns a 404 Not Found error.
    """
    response = client.get("/api/projects/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"

def test_get_all_projects(client: TestClient, db_session: Session):
    """
    Test retrieving all projects.
    """
    # 1. Create a couple of projects
    project1_data = {"name": "Project Alpha"}
    client.post("/api/projects/", json=project1_data)
    
    project2_data = {"name": "Project Beta"}
    client.post("/api/projects/", json=project2_data)
    
    # 2. Get all projects
    response = client.get("/api/projects/")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2 # Using >= to account for other tests' data in the same session
    
    project_names = [p["name"] for p in data]
    assert "Project Alpha" in project_names
    assert "Project Beta" in project_names

def test_update_project(client: TestClient, db_session: Session):
    """
    Test updating an existing project.
    """
    # 1. Create a project
    original_data = {"name": "Original Name", "place_description": "Original Description"}
    create_response = client.post("/api/projects/", json=original_data)
    project_id = create_response.json()["id"]
    
    # 2. Update the project
    updated_data = {"name": "Updated Name", "place_description": "Updated Description"}
    update_response = client.put(f"/api/projects/{project_id}", json=updated_data)
    
    # Verify the update response
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Name"
    
    # 3. Verify the change in the database
    updated_project_in_db = db_session.query(Project).filter(Project.id == project_id).first()
    assert updated_project_in_db.name == "Updated Name"
    assert updated_project_in_db.place_description == "Updated Description"

def test_update_nonexistent_project(client: TestClient):
    """
    Test that updating a project that does not exist returns a 404 Not Found error.
    """
    response = client.put("/api/projects/99999", json={"name": "Won't work"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"

def test_delete_project(client: TestClient, db_session: Session):
    """
    Test deleting an existing project.
    """
    # 1. Create a project
    project_data = {"name": "To Be Deleted"}
    create_response = client.post("/api/projects/", json=project_data)
    project_id = create_response.json()["id"]
    
    # 2. Delete the project
    delete_response = client.delete(f"/api/projects/{project_id}")
    assert delete_response.status_code == 204
    
    # 3. Verify it's gone from the database
    deleted_project = db_session.query(Project).filter(Project.id == project_id).first()
    assert deleted_project is None
    
    # 4. Verify that trying to get it returns 404
    get_response = client.get(f"/api/projects/{project_id}")
    assert get_response.status_code == 404

def test_delete_nonexistent_project(client: TestClient):
    """
    Test that deleting a project that does not exist returns a 404 Not Found error.
    """
    response = client.delete("/api/projects/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"
