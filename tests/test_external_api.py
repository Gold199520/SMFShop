import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from src.services.external_api_service import ExchangeRatesClient, ReviewsService
import json

@pytest.fixture
def mock_httpx_client():
    client = AsyncMock()
    return client

@pytest.mark.asyncio
async def test_exchange_rate_success(mock_httpx_client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"rates": {"USD": 0.013, "EUR": 0.012}}
    mock_httpx_client.get.return_value = mock_response
    
    client = ExchangeRatesClient()
    client.client = mock_httpx_client
    
    rate = await client.get_exchange_rate("RUB", "USD")
    assert rate == 0.013

@pytest.mark.asyncio
async def test_exchange_rate_currency_not_found(mock_httpx_client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"rates": {"EUR": 0.012}}
    mock_httpx_client.get.return_value = mock_response
    
    client = ExchangeRatesClient()
    client.client = mock_httpx_client
    
    rate = await client.get_exchange_rate("RUB", "GBP")
    assert rate is None

@pytest.mark.asyncio
async def test_convert_currency(mock_httpx_client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"rates": {"USD": 0.013}}
    mock_httpx_client.get.return_value = mock_response
    
    client = ExchangeRatesClient()
    client.client = mock_httpx_client
    
    result = await client.convert_currency(1000, "RUB", "USD")
    assert result == 13.0

@pytest.mark.asyncio
async def test_convert_currency_no_rate(mock_httpx_client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"rates": {}}
    mock_httpx_client.get.return_value = mock_response
    
    client = ExchangeRatesClient()
    client.client = mock_httpx_client
    
    result = await client.convert_currency(1000, "RUB", "GBP")
    assert result is None

@pytest.mark.asyncio
async def test_reviews_service_fetch(mock_httpx_client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"user": "Test", "rating": 5}]
    mock_httpx_client.get.return_value = mock_response
    
    service = ReviewsService()
    reviews = await service.fetch_reviews(1, mock_httpx_client)
    assert reviews == [{"user": "Test", "rating": 5}]

@pytest.mark.asyncio
async def test_reviews_service_fetch_error(mock_httpx_client):
    mock_httpx_client.get.side_effect = httpx.RequestError("Connection error")
    
    service = ReviewsService()
    reviews = await service.fetch_reviews(1, mock_httpx_client)
    assert reviews == []

@pytest.mark.asyncio
async def test_reviews_service_post(mock_httpx_client):
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": 1, "review": "Great!"}
    mock_httpx_client.post.return_value = mock_response
    
    service = ReviewsService()
    result = await service.post_review(1, {"review": "Great!"}, mock_httpx_client)
    assert result == {"id": 1, "review": "Great!"}

@pytest.mark.asyncio
async def test_reviews_service_post_error(mock_httpx_client):
    mock_httpx_client.post.side_effect = Exception("Error")
    
    service = ReviewsService()
    result = await service.post_review(1, {"review": "Test"}, mock_httpx_client)
    assert result is None
