import pytest
from src.utils.calculations import calculate_discount, calculate_delivery, get_product_reviews
from unittest.mock import patch, MagicMock

@pytest.mark.parametrize("order_total, expected_discount", [
    (500, 500),      # Нет скидки (<1000)
    (1000, 950),     # 5% скидка: 1000 - 5% = 950
    (5000, 4500),    # 10% скидка: 5000 - 10% = 4500
    (10000, 8000),   # 20% скидка: 10000 - 20% = 8000
])
def test_calculate_discount(order_total, expected_discount):
    """Тест: расчет скидки для разных сумм"""
    assert calculate_discount(order_total) == expected_discount


@pytest.mark.parametrize("order_total, expected_delivery", [
    (500, 500),      # Меньше 1000: платная доставка
    (999, 500),      # Меньше 1000: платная доставка
    (1000, 0),       # Бесплатная доставка
    (5000, 0),       # Бесплатная доставка
    (10000, 0),      # Бесплатная доставка
])
def test_calculate_delivery(order_total, expected_delivery):
    """Тест: расчет доставки для разных сумм"""
    assert calculate_delivery(order_total) == expected_delivery


@patch('src.utils.calculations.requests.get')
def test_get_product_reviews_success(mock_get):
    """Тест: успешное получение отзывов через внешний API"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"user": "Иван", "rating": 5}]
    mock_get.return_value = mock_response

    result = get_product_reviews(1)

    assert result == [{"user": "Иван", "rating": 5}]
    mock_get.assert_called_once_with("https://api.example.com/products/1/reviews")


@patch('src.utils.calculations.requests.get')
def test_get_product_reviews_failure(mock_get):
    """Тест: ошибка при получении отзывов"""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    result = get_product_reviews(999)

    assert result == []