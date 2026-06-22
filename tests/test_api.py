from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
import pytest
import json
from src.api.main import app
from src.api.dependencies import get_db, get_redis, get_current_user

client = TestClient(app)


@pytest.fixture
def mock_user():
    return {"id": 1, "username": "testuser", "email": "test@example.com"}


@pytest.fixture
def mock_product():
    return {
        "id": 1,
        "name": "Тестовый товар",
        "price": 1000.0,
        "stock": 10,
        "category": "test",
        "created_at": "2025-01-01T00:00:00",
        "updated_at": "2025-01-01T00:00:00"
    }


class TestGetProducts:
    """GET /api/v1/products — получение списка товаров"""

    def test_get_products_empty(self):
        mock_db = AsyncMock()
        mock_db.fetchval.return_value = 0
        mock_db.fetch.return_value = []

        mock_redis = AsyncMock()
        mock_redis.get.return_value = None

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_redis] = lambda: mock_redis
        app.dependency_overrides[get_current_user] = lambda: {"id": 1}

        response = client.get("/api/v1/products/")

        assert response.status_code == 200
        assert response.json() == []
        assert mock_db.fetch.called

        app.dependency_overrides.clear()

    def test_get_products_with_data(self, mock_product):
        mock_db = AsyncMock()
        mock_db.fetchval.return_value = 1
        mock_db.fetch.return_value = [mock_product]

        mock_redis = AsyncMock()
        mock_redis.get.return_value = None

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_redis] = lambda: mock_redis
        app.dependency_overrides[get_current_user] = lambda: {"id": 1}

        response = client.get("/api/v1/products/")

        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["name"] == "Тестовый товар"

        app.dependency_overrides.clear()

    def test_get_products_from_cache(self, mock_product):
        mock_db = AsyncMock()
        mock_redis = AsyncMock()
        mock_redis.get.return_value = json.dumps([mock_product])

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_redis] = lambda: mock_redis
        app.dependency_overrides[get_current_user] = lambda: {"id": 1}

        response = client.get("/api/v1/products/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Тестовый товар"
        assert not mock_db.fetch.called

        app.dependency_overrides.clear()


class TestCreateOrder:
    """POST /api/v1/orders — создание заказа"""

    def test_create_order_success(self):
        app.dependency_overrides[get_current_user] = lambda: {"id": 1}

        response = client.post("/api/v1/orders/?user_id=1")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"
        assert "order_id" in data

        app.dependency_overrides.clear()

    def test_create_order_without_auth(self):
        app.dependency_overrides.clear()
        response = client.post("/api/v1/orders/?user_id=1")
        assert response.status_code == 401


class TestGetProduct:
    """GET /api/v1/products/{id} — получение товара по ID"""

    def test_get_product_by_id_success(self, mock_product):
        mock_db = AsyncMock()
        mock_db.fetchrow.return_value = mock_product

        mock_redis = AsyncMock()
        mock_redis.get.return_value = None

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_redis] = lambda: mock_redis
        app.dependency_overrides[get_current_user] = lambda: {"id": 1}

        response = client.get("/api/v1/products/1")

        assert response.status_code == 200
        assert response.json()["name"] == "Тестовый товар"

        app.dependency_overrides.clear()

    def test_get_product_not_found(self):
        mock_db = AsyncMock()
        mock_db.fetchrow.return_value = None

        mock_redis = AsyncMock()
        mock_redis.get.return_value = None

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_redis] = lambda: mock_redis
        app.dependency_overrides[get_current_user] = lambda: {"id": 1}

        response = client.get("/api/v1/products/999")

        assert response.status_code == 404
        assert "не найден" in response.json()["detail"]

        app.dependency_overrides.clear()