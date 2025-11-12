import uuid
import requests

BASE_URL = "http://localhost:8000/api"

# def generate_external_userid():
#     return str(uuid.uuid4())
#
# def login_or_create_user(external_user_id: str):
#     headers = {"X-User-ID": external_user_id}
#     response = requests.post(f"{BASE_URL}/users/login", headers=headers)
#     response.raise_for_status()
#     return response.json()
#
# def test_create_global_role(external_user_id: str, user_internal_id: int, global_role_type: str):
#     headers = {
#         "Content-Type": "application/json",
#         "X-User-ID": external_user_id
#     }
#     payload = {
#         "user_id": user_internal_id,
#         "role": global_role_type
#     }
#     response = requests.post(f"{BASE_URL}/roles/global", headers=headers, json=payload)
#     return response
#
# def test_get_global_role_success():
#     # Arrange
#     global_role_types = ["client", "worker"]
#
#
#     for global_role_type in global_role_types:
#         external_user_id = generate_external_userid()
#         headers = {
#             "Content-Type": "application/json",
#             "X-User-ID": external_user_id
#         }
#         payload = {
#             "user_id": user_internal_id,
#             "role": global_role_type
#         }
#         response = requests.post(f"{BASE_URL}/roles/global", headers=headers, json=payload)
#
#
#         # Act
#         headers = {
#             "Content-Type": "application/json",
#             "X-User-ID": external_user_id
#         }
        # response = requests.get(f"{BASE_URL}/roles/global/{user_internal_id}", headers=headers)
        #
        # # Assert
        # assert response.status_code == 200
        # response_data = response.json()
        # assert response_data["message"] == "Global role retrieved successfully"
        # assert response_data["data"]["user_id"] == user_internal_id
        # assert response_data["data"]["role_type"] == "client"
