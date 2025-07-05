import requests
import json
import uuid
from app.models.role_model import RoleType

# Base URL of your FastAPI application
BASE_URL = "http://localhost:8000"  # Adjust this if your server is running on a different port or host

# Generate a random user ID
user_id = str(uuid.uuid4())

# Headers to be used in all requests
headers = {
    "Content-Type": "application/json",
    "X-User-ID": user_id
}

def get_client_role():
    """Assign client role to the user"""
    url = f"{BASE_URL}/api/roles"
    payload = {"role_type": RoleType.CLIENT.value}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print("Successfully obtained client role")
    else:
        print(f"Failed to obtain client role: {response.text}")
        exit(1)

def create_list():
    """Create a new list"""
    url = f"{BASE_URL}/api/lists"
    payload = {
        "list_create": {  # Wrap the payload in 'list_create'
            "name": "My New List",
            "description": "This is a test list created by a script"
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        list_data = response.json()["data"]
        print(f"Successfully created list: {list_data['name']} (ID: {list_data['id']})")
    else:
        print(f"Failed to create list: {response.text}")

if __name__ == "__main__":
    get_client_role()
    create_list()