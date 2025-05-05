import pytest
from httpx import AsyncClient


# Тест на получение списка пользователей (если роль admin)
@pytest.mark.asyncio
async def test_get_users_list_success():
    async with AsyncClient(base_url="http://localhost:8002") as ac:
        response = await ac.get("/admin/users/", headers={"x-role": "admin"})

    assert response.status_code == 200
    assert isinstance(response.json(), list)


# Тест на блокировку пользователя (если роль admin)
@pytest.mark.asyncio
async def test_block_user_success():
    async with AsyncClient(base_url="http://localhost:8002") as ac:
        response = await ac.post("/admin/users/1/block", headers={"x-role": "admin"})

    assert response.status_code == 200
    assert "message" in response.json()


# Тест на разблокировку пользователя (мок Auth Service)
@pytest.mark.asyncio
async def test_unblock_user_success(monkeypatch):
    monkeypatch.setattr(
        "httpx.AsyncClient.post",
        lambda self, url, *args, **kwargs: type("Response", (), {
            "status_code": 200,
            "json": lambda: {"message": "User 1 unblocked"}
        })()
    )

    async with AsyncClient(base_url="http://localhost:8002") as ac:
        response = await ac.post("/admin/users/1/unblock", headers={"x-role": "admin"})

    assert response.status_code == 200
    assert response.json() == {"message": "User 1 unblocked"}


# Тест на смену роли пользователя (мок Auth Service)
@pytest.mark.asyncio
async def test_change_user_role_success(monkeypatch):
    monkeypatch.setattr(
        "httpx.AsyncClient.patch",
        lambda self, url, *args, **kwargs: type("Response", (), {
            "status_code": 200,
            "json": lambda: {"message": "User 1 role changed to moderator"}
        })()
    )

    async with AsyncClient(base_url="http://localhost:8002") as ac:
        response = await ac.patch(
            "/admin/users/1/role?new_role=moderator",
            headers={"x-role": "admin"}
        )

    assert response.status_code == 200
    assert response.json() == {"message": "User 1 role changed to moderator"}


# Тест на блокировку с неадминской ролью (ожидается 403)
@pytest.mark.asyncio
async def test_block_user_forbidden_for_non_admin():
    async with AsyncClient(base_url="http://localhost:8002") as ac:
        response = await ac.post("/admin/users/1/block", headers={"x-role": "user"})

    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied"


# Тест на удаление поста (успешный сценарий)
@pytest.mark.asyncio
async def test_delete_post_success(monkeypatch):
    # Мокаем удаление поста (предположим, что Post Service вернёт 200)
    monkeypatch.setattr(
        "httpx.AsyncClient.delete",
        lambda self, url, *args, **kwargs: type("Response", (), {
            "status_code": 200,
            "json": lambda: {"message": "Post 1 deleted"}
        })()
    )

    async with AsyncClient(base_url="http://localhost:8002") as ac:
        response = await ac.delete("/admin/posts/1", headers={"x-role": "admin"})

    assert response.status_code == 200
    assert response.json() == {"message": "Post 1 deleted"}


# Тест на удаление комментария (успешный сценарий)
@pytest.mark.asyncio
async def test_delete_comment_success(monkeypatch):
    # Мокаем удаление комментария (предположим, что Post Service вернёт 200)
    monkeypatch.setattr(
        "httpx.AsyncClient.delete",
        lambda self, url, *args, **kwargs: type("Response", (), {
            "status_code": 200,
            "json": lambda: {"message": "Comment 1 deleted"}
        })()
    )

    async with AsyncClient(base_url="http://localhost:8002") as ac:
        response = await ac.delete("/admin/comments/1", headers={"x-role": "admin"})

    assert response.status_code == 200
    assert response.json() == {"message": "Comment 1 deleted"}


# Тест на получение статистики пользователей и постов
@pytest.mark.asyncio
async def test_get_admin_stats_success(monkeypatch):
    # Мокаем ответ от сервиса статистики
    monkeypatch.setattr(
        "httpx.AsyncClient.get",
        lambda self, url, *args, **kwargs: type("Response", (), {
            "status_code": 200,
            "json": lambda: {
                "total_users": 100,
                "active_users": 90,
                "banned_users": 10,
                "total_posts": 200,
                "total_comments": 500
            }
        })()
    )

    async with AsyncClient(base_url="http://localhost:8002") as ac:
        response = await ac.get("/admin/stats", headers={"x-role": "admin"})

    assert response.status_code == 200
    stats = response.json()
    assert "total_users" in stats
    assert "active_users" in stats
    assert "banned_users" in stats
    assert "total_posts" in stats
    assert "total_comments" in stats
