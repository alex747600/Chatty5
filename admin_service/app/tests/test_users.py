import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch
import jwt
from datetime import datetime, timedelta

client = TestClient(app)

# Mock JWT token for admin (role 0)
def create_token(user_id: int, role: int):
    payload = {
        "sub": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, "your-secret-key", algorithm="HS256")

admin_token = create_token(1, 0)
user_token = create_token(2, 1)

# Mock Auth Service responses
mock_users = [
    {"id": 1, "username": "admin", "email": "admin@example.com", "role": 0, "is_blocked": False},
    {"id": 2, "username": "user", "email": "user@example.com", "role": 1, "is_blocked": False}
]

@patch("requests.get")
def test_list_users_success(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_users
    response = client.get("/admin/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json() == {"users": mock_users}

@patch("requests.get")
def test_list_users_unauthorized(mock_get):
    response = client.get("/admin/users", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"

@patch("requests.post")
def test_block_user_success(mock_post):
    mock_post.return_value.status_code = 200
    response = client.post("/admin/users/2/block", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "User 2 blocked"

@patch("requests.post")
def test_unblock_user_success(mock_post):
    mock_post.return_value.status_code = 200
    response = client.post("/admin/users/2/unblock", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "User 2 unblocked"

@patch("requests.patch")
def test_update_role_success(mock_patch):
    mock_patch.return_value.status_code = 200
    response = client.patch(
        "/admin/users/2/role",
        json={"role": 1},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "User 2 role updated to 1"

@patch("requests.patch")
def test_update_role_invalid(mock_patch):
    response = client.patch(
        "/admin/users/2/role",
        json={"role": 3},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Role must be 0, 1, or 2"

@patch("requests.delete")
def test_delete_user_success(mock_delete):
    mock_delete.return_value.status_code = 200
    response = client.delete(
        "/admin/users/2",
        json={"reason": "Violation of terms"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "User 2 deleted"