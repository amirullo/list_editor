import requests
import json
import uuid

# Base URL of your FastAPI application
BASE_URL = "http://localhost:8000"  # Adjust this if your server is running on a different port or host

# Generate a random user ID
user_id = str(uuid.uuid4())

# Headers to be used in all requests
headers = {
    "Content-Type": "application/json",
    "X-User-ID": user_id
}

def get_worker_role():
    """Assign worker role to the user"""
    url = f"{BASE_URL}/api/roles"
    payload = {"role_type": "worker"}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print("Successfully obtained worker role")
    else:
        print(f"Failed to obtain worker role: {response.text}")
        exit(1)

def get_all_lists():
    """Get all lists"""
    url = f"{BASE_URL}/api/lists"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["data"]
    else:
        print(f"Failed to get lists: {response.text}")
        exit(1)

def edit_list(list_id):
    """Edit an existing list"""
    url = f"{BASE_URL}/api/lists/{list_id}"
    
    # First, acquire a lock
    lock_url = f"{BASE_URL}/api/lists/{list_id}/lock"
    lock_response = requests.post(lock_url, headers=headers)
    if lock_response.status_code != 200:
        print(f"Failed to acquire lock: {lock_response.text}")
        return

    try:
        # Update the list
        payload = {
            "name": "Updated List Name",
            "description": "This list was updated by a script"
        }
        response = requests.put(url, headers=headers, json=payload)
        if response.status_code == 200:
            list_data = response.json()["data"]
            print(f"Successfully updated list: {list_data['name']} (ID: {list_data['id']})")
        else:
            print(f"Failed to update list: {response.text}")
    finally:
        # Always release the lock, even if the update failed
        release_response = requests.delete(lock_url, headers=headers)
        if release_response.status_code != 200:
            print(f"Failed to release lock: {release_response.text}")

if __name__ == "__main__":
    get_worker_role()
    lists = get_all_lists()
    if lists:
        list_to_edit = lists[0]  # Edit the first list
        edit_list(list_to_edit['id'])
    else:
        print("No lists available to edit")
