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

@patch("requests.post")
def test_block_user_logs(mock_post, db: Session):
    mock_post.return_value.status_code = 200
    response = client.post("/admin/users/2/block", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    log = db.query(AuditLog).filter(AuditLog.action == "block_user", AuditLog.target_id == 2).first()
    assert log is not None
    assert log.admin_id == 1
    assert log.action == "block_user"
    assert log.target_id == 2

@patch("requests.delete")
def test_delete_post_logs(mock_delete, db: Session):
    mock_delete.return_value.status_code = 200
    response = client.delete("/admin/posts/1", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    log = db.query(AuditLog).filter(AuditLog.action == "delete_post", AuditLog.target_id == 1).first()
    assert log is not None
    assert log.admin_id == 1
    assert log.action == "delete_post"
    assert log.target_id == 1

@patch("requests.delete")
def test_delete_user_logs(mock_delete, db: Session):
    mock_delete.return_value.status_code = 200
    response = client.delete(
        "/admin/users/2",
        json={"reason": "Violation of terms"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    log = db.query(AuditLog).filter(AuditLog.action == "delete_user", AuditLog.target_id == 2).first()
    assert log is not None
    assert log.admin_id == 1
    assert log.action == "delete_user"
    assert log.target_id == 2
    assert log.reason == "Violation of terms"

def test_list_logs_success(db: Session):
    # Add a sample log
    log = AuditLog(
        admin_id=1,
        action="test_action",
        target_id=999,
        timestamp=datetime.utcnow()
    )
    db.add(log)
    db.commit()
    response = client.get("/admin/logs", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert len(response.json()["logs"]) >= 1

def test_list_logs_unauthorized():
    response = client.get("/admin/logs", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"