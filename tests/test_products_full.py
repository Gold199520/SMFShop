import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.api.dependencies import get_db, get_redis, get_current_user
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
import json

client = TestClient(app)

@pytest.fixture(autouse=True)
def override_dependencies():
    """Автоматически подменяем зависимости перед каждым тестом"""
    mock_db = AsyncMock()
    mock_db.fetchrow.return_value = {
        "id": 1, "name": "Test Product", "price": 99.99, "stock": 50,
        "category": "electronics", "description": "A test product",
        "created_at": datetime.now(), "updated_at": None
    }
    mock_db.fetch.return_value = [
        {"id": 1, "name": "Test", "price": 99.99, "stock": 50, 
         "category": "electronics", "description": "Test",
         "created_at": datetime.now(), "updated_at": None}
    ]
    mock_db.fetchval.return_value = 1
    mock_db.execute.return_value = "DELETE 1"
    
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.setex = AsyncMock()
    mock_redis.delete = AsyncMock()
    mock_redis.keys = AsyncMock(return_value=[])
    
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_redis] = lambda: mock_redis
    app.dependency_overrides[get_current_user] = lambda: {"id": 1, "username": "test", "email": "test@test.com"}
    
    yield
    
    app.dependency_overrides.clear()


def test_get_all_products():
    """GET /api/v1/products/ - список товаров"""
    response = client.get("/api/v1/products/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_products_with_pagination():
    """GET /api/v1/products/?page=1&limit=10"""
    response = client.get("/api/v1/products/?page=1&limit=10")
    assert response.status_code == 200


def test_get_products_by_category():
    """GET /api/v1/products/?category=electronics"""
    response = client.get("/api/v1/products/?category=electronics")
    assert response.status_code == 200


def test_get_single_product():
    """GET /api/v1/products/1"""
    response = client.get("/api/v1/products/1")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Product"


def test_get_product_not_found():
    """GET /api/v1/products/999 - не найден"""
    db_mock = app.dependency_overrides[get_db]()
    db_mock.fetchrow.return_value = None
    
    response = client.get("/api/v1/products/999")
    assert response.status_code == 404


def test_create_product():
    """POST /api/v1/products/ - создание товара"""
    response = client.post("/api/v1/products/", json={
        "name": "New Product",
        "price": 49.99,
        "stock": 100,
        "category": "books",
        "description": "New book"
    })
    assert response.status_code == 201


def test_update_product():
    """PUT /api/v1/products/1 - обновление товара"""
    response = client.put("/api/v1/products/1", json={
        "name": "Updated Product",
        "price": 149.99
    })
    assert response.status_code == 200


def test_delete_product():
    """DELETE /api/v1/products/1 - удаление товара"""
    response = client.delete("/api/v1/products/1")
    assert response.status_code == 204
