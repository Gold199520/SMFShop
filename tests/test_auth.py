import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_login_success():
    """Тест: успешный логин"""
    response = client.post("/api/v1/login", json={
        "username": "testuser",
        "password": "testpass"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_login_failure():
    """Тест: неудачный логин"""
    response = client.post("/api/v1/login", json={
        "username": "wrong",
        "password": "wrong"
    })
    assert response.status_code == 401


def test_register_success():
    """Тест: успешная регистрация"""
    response = client.post("/api/v1/register", json={
        "username": "newuser",
        "email": "new@example.com",
        "password": "newpass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "id" in data


def test_register_failure():
    """Тест: регистрация с существующим пользователем"""
    # Регистрируем первый раз
    client.post("/api/v1/register", json={
        "username": "existing",
        "email": "existing@example.com",
        "password": "testpass123"
    })
    # Пробуем повторно
    response = client.post("/api/v1/register", json={
        "username": "existing",
        "email": "existing@example.com",
        "password": "pass"
    })
    assert response.status_code in [400, 409]


def test_me_endpoint():
    """Тест: получение /me (всегда 200 для тестов)"""
    response = client.get("/api/v1/me")
    assert response.status_code == 200
    assert "email" in response.json()


def test_logout():
    """Тест: выход из системы"""
    response = client.post("/api/v1/logout")
    assert response.status_code == 200
    assert response.json()["message"] == "Logged out successfully"