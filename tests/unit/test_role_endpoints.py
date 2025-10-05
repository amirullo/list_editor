import pytest
import uuid
import requests
import asyncio


BASE_URL = "http://localhost:8000"

def generate_userid():
    user_id = str(uuid.uuid4())
    return user_id

def create_global_role(test_user_id):
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": test_user_id
    }
    payload = {
        "current_user_id": test_user_id,
        "role": "client"
    }
    response = requests.post(f"{BASE_URL}/api/roles/global", headers=headers, json=payload)
    return response


def test_get_global_role_success():
    test_user_id = generate_userid()
    create_response = create_global_role(test_user_id)

    if create_response.status_code != 200:
        pytest.fail(f"Expected status code 200, but got {create_response.status_code}. Error detail: {create_response.text}")

    data = create_response.json()
    assert data["status"] == "success"
    assert data["message"] == "Global role created successfully"
    assert data["data"]["user_id"] == test_user_id
    assert data["data"]["role_type"] == "client"

    # Now, retrieve the global role
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": test_user_id
    }
    response = requests.get(f"{BASE_URL}/api/roles/global/{test_user_id}", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Global role retrieved successfully"
    assert data["data"]["user_id"] == test_user_id
    assert data["data"]["role_type"] == "client"



# @pytest.mark.asyncio
# async def make_fake_request(test_user_id):
#     headers = {
#         "Content-Type": "application/json",
#         "X-User-ID": test_user_id
#     }
#     response = requests.get(f"{BASE_URL}/api/roles/global/{test_user_id}", headers=headers)
#     return response.status_code
#
# @pytest.mark.asyncio
# async def make_correct_request(test_user_id):
#     create_global_role(test_user_id)
#     headers = {
#         "Content-Type": "application/json",
#         "X-User-ID": test_user_id
#     }
#     response = requests.get(f"{BASE_URL}/api/roles/global/{test_user_id}", headers=headers)
#     return response.status_code
#
# @pytest.mark.asyncio
# async def test_get_global_role_concurrent_performance():
#     num_requests = 1000
#     user_ids = [generate_userid() for _ in range(num_requests)]
#
#     start_time = asyncio.get_event_loop().time()
#     responses = await asyncio.gather(*[make_fake_request(user_id) for user_id in user_ids])
#     end_time = asyncio.get_event_loop().time()
#
#     total_time = end_time - start_time
#     avg_response_time = total_time / num_requests
#
#     assert avg_response_time < 0.1, f"Average response time ({avg_response_time:.3f}s) exceeded 0.1s threshold"
#     assert all(status == 404 for status in responses), "All responses should be 404 (Not Found) for non-existent roles"
#
#     print(f"")
#     print(f"Average response time for fake user_id's: {avg_response_time:.3f} seconds")
#
#     # Now, test with correct requests
#     start_time = asyncio.get_event_loop().time()
#     responses = await asyncio.gather(*[make_correct_request(user_id) for user_id in user_ids])
#     end_time = asyncio.get_event_loop().time()
#
#     total_time = end_time - start_time
#     avg_response_time = total_time / num_requests
#
#     assert avg_response_time < 0.1, f"Average response time ({avg_response_time:.3f}s) exceeded 0.1s threshold"
#     assert all(status == 200 for status in responses), "All responses should be 200(ok) for existent roles"
#
#     print(f"Average response time with creation user_id's: {avg_response_time:.3f} seconds")
