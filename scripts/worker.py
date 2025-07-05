import requests
import json
import uuid
from app.models.role_model import RoleType
import time

BASE_URL = "http://localhost:8000"
user_id = str(uuid.uuid4())

headers = {
    "Content-Type": "application/json",
    "X-User-ID": user_id
}

def get_worker_role():
    """Assign worker role to the user"""
    url = f"{BASE_URL}/api/roles"
    payload = {"role_type": RoleType.WORKER.value}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print("Successfully obtained worker role")
    else:
        print(f"Failed to obtain worker role: {response.text}")
        exit(1)

def get_current_role():
    url = f"{BASE_URL}/api/roles"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("Successfully obtained role info")
        print(response.json()["data"])
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

def get_specific_list(list_id):
    url = f"{BASE_URL}/api/lists/{list_id}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["data"]
    else:
        print(f"Failed to get lists: {response.text}")
        exit(1)

def delete_list(list_id):
    """Delete a list"""
    url = f"{BASE_URL}/api/lists/{list_id}"
    response = requests.delete(url, headers=headers)
    if response.status_code == 200:
        print(f"Successfully deleted list with ID: {list_id}")
    else:
        print(f"Failed to delete list: {response.text}")
        exit(1)

def get_notifications():
    """Fetch notifications"""
    url = f"{BASE_URL}/api/sync/notifications"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        notifications = response.json()
        print("Notifications:")
        for notification in notifications:
            print(f"- {notification}")
    else:
        print(f"Failed to fetch notifications: {response.text}")


def add_item(list_id, item_name, quantity, price):
    """Add an item to a list"""
    url = f"{BASE_URL}/api/lists/{list_id}/items"
    payload = {
        "name": item_name,
        "quantity": quantity,
        "price": price
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        item_data = response.json()["data"]
        print(f"Successfully added item: {item_data['name']} (ID: {item_data['item_id']})")
    else:
        print(f"Failed to add item: {response.text}")
        exit(1)

def update_item(item_id, item_update):
    url = f"{BASE_URL}/api/items/{item_id}"
    response = requests.put(url, headers=headers, json=item_update.dict())
    if response.status_code == 200:
        print("Successfully updated item")
    else:
        print(f"Failed to update item: {response.text}")
        exit(1)

if __name__ == "__main__":
    get_worker_role()
    get_current_role()
    lists = get_all_lists()
    open_list_ids = [x['id'] for x in lists]
    print("All lists: {}".format(open_list_ids))

    if lists:
        list_to_edit = lists[0]  # Edit the first list
        list_data = get_specific_list(list_to_edit['id'])
        print(f"Successfully retrieved list info: {list_data}")
        add_item(list_to_edit['id'], "New Item", 10, 10.99)

        list_data = get_specific_list(list_to_edit['id'])
        print(f"Updated info in list: {list_data}")

        # update_item(list_to_edit['id'], {"name": "Updated Item"})
        # print(f"Successfully updated item: {item_to_update['name']}")

        delete_list(list_to_edit['id'])
    else:
        print("No lists available to edit")

    lists = get_all_lists()
    open_list_ids = [x['id'] for x in lists]
    print("All lists: {}".format(open_list_ids))
    print("Waiting a few seconds for the notification to be processed...")
    time.sleep(2)
    print("Checking for notifications:")
    get_notifications()

