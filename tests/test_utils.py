import pytest
from src.utils.calculations import calculate_discount, calculate_delivery, get_product_reviews
from unittest.mock import patch, MagicMock

@pytest.mark.parametrize("order_total, expected_discount", [
    (500, 500),
    (1000, 950),
    (5000, 4500),
    (10000, 8000),
])
def test_calculate_discount(order_total, expected_discount):
    assert calculate_discount(order_total) == expected_discount


@pytest.mark.parametrize("order_total, expected_delivery", [
    (500, 500),
    (999, 500),
    (1000, 0),
    (5000, 0),
    (10000, 0),
])
def test_calculate_delivery(order_total, expected_delivery):
    assert calculate_delivery(order_total) == expected_delivery


@patch('httpx.get')
def test_get_product_reviews_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"user": "Иван", "rating": 5}]
    mock_get.return_value = mock_response

    result = get_product_reviews(1)
    assert result == [{"user": "Иван", "rating": 5}]


@patch('httpx.get')
def test_get_product_reviews_failure(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    result = get_product_reviews(999)
    assert result == []
