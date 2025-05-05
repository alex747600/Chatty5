import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch
import jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import AuditLog

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

mock_user_stats = {
    "total_users": 100,
    "blocked_users": 10,
    "active_users": 90
}

mock_post_stats = {
    "total_posts": 500,
    "total_comments": 1000
}


@patch("requests.get")
def test_get_stats_success(mock_get, db: Session):
    def mock_get_side_effect(url):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code

            def json(self):
                return self.json_data

            def raise_for_status(self):
                if self.status_code != 200:
                    raise requests.RequestException

        if "auth_service" in url:
            return MockResponse(mock_user_stats, 200)
        if "post_service" in url:
            return MockResponse(mock_post_stats, 200)
        return MockResponse({}, 404)

    mock_get.side_effect = mock_get_side_effect
    response = client.get("/admin/stats", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json() == {
        "total_users": 100,
        "blocked_users": 10,
        "active_users": 90,
        "total_posts": 500,
        "total_comments": 1000
    }
    log = db.query(AuditLog).filter(AuditLog.action == "view_stats").first()
    assert log is not None
    assert log.admin_id == 1
    assert log.action == "view_stats"
    assert log.target_id == 0


@patch("requests.get")
def test_get_stats_unauthorized(mock_get):
    response = client.get("/admin/stats", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


@patch("requests.get")
def test_get_stats_service_unavailable(mock_get):
    mock_get.side_effect = requests.RequestException("Service down")
    response = client.get("/admin/stats", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 503
    assert response.json()["detail"] == "Service unavailable"