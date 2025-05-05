import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch
import jwt
from datetime import datetime, timedelta

client = TestClient(app)

def create_token(user_id: int, role: int):
    payload = {
        "sub": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, "your-secret-key", algorithm="HS256")

admin_token = create_token(1, 0)
user_token = create_token(2, 1)

mock_reports = [
    {"id": 1, "post_id": 1, "comment_id": None, "reason": "Spam", "reported_by": 2, "timestamp": "2025-04-29T10:00:00Z"}
]

@patch("requests.get")
def test_list_reports_success(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_reports
    response = client.get("/admin/reports", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json() == {"reports": mock_reports}

@patch("requests.get")
def test_list_reports_unauthorized(mock_get):
    response = client.get("/admin/reports", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"

@patch("requests.delete")
def test_delete_post_success(mock_delete):
    mock_delete.return_value.status_code = 200
    response = client.delete("/admin/posts/1", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "Post 1 deleted"

@patch("requests.delete")
def test_delete_post_not_found(mock_delete):
    mock_delete.return_value.status_code = 404
    response = client.delete("/admin/posts/999", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"

@patch("requests.delete")
def test_delete_comment_success(mock_delete):
    mock_delete.return_value.status_code = 200
    response = client.delete("/admin/comments/1", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "Comment 1 deleted"

@patch("requests.delete")
def test_delete_comment_not_found(mock_delete):
    mock_delete.return_value.status_code = 404
    response = client.delete("/admin/comments/999", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Comment not found"