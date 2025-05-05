import pytest
from fastapi.testclient import TestClient
from app.main import app
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

@pytest.mark.asyncio
async def test_user_management_integration(db: Session):
    # Test blocking a user
    response = client.post("/admin/users/2/block", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "User 2 blocked"
    log = db.query(AuditLog).filter(AuditLog.action == "block_user", AuditLog.target_id == 2).first()
    assert log is not None
    assert log.admin_id == 1

    # Test unblocking a user
    response = client.post("/admin/users/2/unblock", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "User 2 unblocked"

    # Test changing user role
    response = client.patch(
        "/admin/users/2/role",
        json={"role": 1},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "User 2 role updated to 1"

    # Test deleting a user
    response = client.delete(
        "/admin/users/2",
        json={"reason": "Violation of terms"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "User 2 deleted"
    log = db.query(AuditLog).filter(AuditLog.action == "delete_user", AuditLog.target_id == 2).first()
    assert log.reason == "Violation of terms"

@pytest.mark.asyncio
async def test_content_moderation_integration(db: Session):
    # Test deleting a post
    response = client.delete("/admin/posts/1", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "Post 1 deleted"
    log = db.query(AuditLog).filter(AuditLog.action == "delete_post", AuditLog.target_id == 1).first()
    assert log is not None

    # Test deleting a comment
    response = client.delete("/admin/comments/1", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "Comment 1 deleted"
    log = db.query(AuditLog).filter(AuditLog.action == "delete_comment", AuditLog.target_id == 1).first()
    assert log is not None

@pytest.mark.asyncio
async def test_stats_integration(db: Session):
    response = client.get("/admin/stats", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    stats = response.json()
    assert "total_users" in stats
    assert "blocked_users" in stats
    assert "active_users" in stats
    assert "total_posts" in stats
    assert "total_comments" in stats
    log = db.query(AuditLog).filter(AuditLog.action == "view_stats").first()
    assert log is not None

@pytest.mark.asyncio
async def test_user_activity_integration(db: Session):
    response = client.get("/admin/activity", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    stats = response.json()
    assert "total_active_users" in stats
    assert "posts_created" in stats
    assert "comments_created" in stats
    log = db.query(AuditLog).filter(AuditLog.action == "view_user_activity").first()
    assert log is not None

@pytest.mark.asyncio
async def test_negative_scenarios():
    # Test non-existent user
    response = client.post("/admin/users/999/block", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 503  # Assuming Auth Service returns error

    # Test non-existent post
    response = client.delete("/admin/posts/999", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"