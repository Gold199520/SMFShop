# Подход к тестированию в проекте SFMShop

## Обзор

В проекте SFMShop используется модульное и интеграционное тестирование. Написано 34 теста (24 модульных + 10 API). Инструмент: pytest + pytest-cov + unittest.mock + httpx.

## Типы тестов

### Unit-тесты (24 теста)
- tests/test_models.py (15 тестов): Product, User, Order
- tests/test_utils.py (9 тестов): calculate_discount, calculate_delivery
- Инструменты: фикстуры, параметризация

### Integration-тесты (10 тестов)
- tests/test_urls.py: GET/POST /api/v1/products/, /orders/, /users/
- Особенности: автономное FastAPI-приложение, моки БД и внешних API

## Инструменты и практики

### Инструменты
- pytest — запуск тестов
- pytest-cov — покрытие кода
- unittest.mock — моки
- httpx — HTTP-клиент для тестов

### Практики
- TDD — функции calculate_discount, calculate_delivery написаны после тестов
- Фикстуры — sample_product, sample_user, sample_order
- Параметризация — проверка скидок и доставки с разными суммами
- Моки — @patch для asyncpg и httpx

## Покрытие кода

- Критичная бизнес-логика: >80%
- Функции расчёта: 100%
- Классы моделей: >80%
- API endpoints: >70%

## Примеры тестов

### Unit-тест с параметризацией (test_utils.py)

@pytest.mark.parametrize("order_total, expected_discount", [
    (500, 500),
    (1000, 950),
    (5000, 4500),
    (10000, 8000),
])
def test_calculate_discount(order_total, expected_discount):
    assert calculate_discount(order_total) == expected_discount

### Unit-тест с фикстурой (test_models.py)

def test_product_reduce_quantity(sample_product):
    sample_product.reduce_quantity(3)
    assert sample_product.quantity == 7

### Integration-тест с моком (test_urls.py)

@patch("httpx.AsyncClient.get", new_callable=AsyncMock)
def test_mock_external_api(self, mock_get):
    mock_get.return_value.json.return_value = {"review": "Отличный товар!"}
    mock_get.return_value.status_code = 200
    response = client.get("/api/v1/products/1")
    assert response.status_code == 200

## Заключение

Тестирование в SFMShop построено на TDD, моках, фикстурах и параметризации. 34 теста покрывают модели, бизнес-логику и API.