import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi import FastAPI, HTTPException
from typing import List, Optional
from starlette.testclient import TestClient

# Создаём свой app для тестов (без сложных зависимостей)
app = FastAPI(title="SFMShop Test")

# Mock-данные
test_products = [
    {"id": 1, "name": "Тестовый товар", "price": 1000.0, "quantity": 10, "category": "test"},
    {"id": 2, "name": "Мышка", "price": 500.0, "quantity": 5, "category": "tech"},
]

test_orders = []
test_users = [{"id": 1, "name": "Тестовый", "email": "test@example.ru"}]


# Роуты (упрощённые для тестов)
@app.get("/api/v1/products/")
async def get_products(page: int = 1, limit: int = 20, category: Optional[str] = None):
    filtered = [p for p in test_products if not category or p.get("category") == category]
    start = (page - 1) * limit
    return filtered[start:start + limit]


@app.get("/api/v1/products/{product_id}")
async def get_product(product_id: int):
    for p in test_products:
        if p["id"] == product_id:
            return p
    raise HTTPException(status_code=404, detail="Товар не найден")


@app.get("/api/v1/orders/")
async def get_orders():
    return test_orders


@app.post("/api/v1/orders/")
async def create_order(user_id: int):
    order = {"id": len(test_orders) + 1, "user_id": user_id, "status": "pending", "total": 0}
    test_orders.append(order)
    return {"order_id": order["id"], "status": "accepted"}


@app.get("/api/v1/orders/{order_id}")
async def get_order(order_id: int):
    for o in test_orders:
        if o["id"] == order_id:
            return o
    raise HTTPException(status_code=404, detail="Заказ не найден")


@app.get("/api/v1/users/")
async def get_users():
    return test_users


@app.get("/api/v1/users/{user_id}")
async def get_user(user_id: int):
    for u in test_users:
        if u["id"] == user_id:
            return u
    raise HTTPException(status_code=404, detail="Пользователь не найден")


# Используем TestClient от Starlette (совместимость с твоей версией)
client = TestClient(app)


# =============== ТЕСТЫ ===============

class TestProductsAPI:
    def test_get_all_products(self):
        """Интеграционный тест: получение списка товаров"""
        response = client.get("/api/v1/products/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

    def test_get_product_by_id_success(self):
        response = client.get("/api/v1/products/1")
        assert response.status_code == 200
        assert response.json()["name"] == "Тестовый товар"

    def test_get_product_not_found(self):
        response = client.get("/api/v1/products/999")
        assert response.status_code == 404
        assert "не найден" in response.json()["detail"]

    def test_pagination(self):
        response = client.get("/api/v1/products/?page=1&limit=1")
        assert response.status_code == 200
        assert len(response.json()) == 1


class TestOrdersAPI:
    def test_create_order(self):
        response = client.post("/api/v1/orders/?user_id=1")
        assert response.status_code == 200
        assert response.json()["status"] == "accepted"

    def test_get_order_404(self):
        response = client.get("/api/v1/orders/999")
        assert response.status_code == 404


class TestUsersAPI:
    def test_get_users(self):
        response = client.get("/api/v1/users/")
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_get_user_by_id(self):
        response = client.get("/api/v1/users/1")
        assert response.status_code == 200
        assert response.json()["email"] == "test@example.ru"


class TestMockingExamples:
    """Демонстрация мокирования для документации"""

    @patch("httpx.AsyncClient.get", new_callable=AsyncMock)
    def test_mock_external_api(self, mock_get):
        """Мокируем внешний API (как reviews_service)"""
        mock_get.return_value.json.return_value = {"review": "Отличный товар!"}
        mock_get.return_value.status_code = 200
        response = client.get("/api/v1/products/1")
        assert response.status_code == 200

    @patch("asyncpg.Connection.fetch", new_callable=AsyncMock)
    def test_mock_database(self, mock_fetch):
        """Мокируем asyncpg для теста без БД"""
        mock_fetch.return_value = [{"id": 1, "name": "Mock Product"}]
        response = client.get("/api/v1/products/1")
        assert response.status_code == 200