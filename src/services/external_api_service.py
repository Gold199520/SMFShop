import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
import logging
from typing import Optional, Dict, Any
import asyncio

logger = logging.getLogger(__name__)


class ExchangeRatesClient:
    """Клиент для работы с API курсов валют"""

    def __init__(self, base_url: str = "https://api.exchangerate-api.com/v4"):
        self.base_url = base_url
        self.client = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
            limits=httpx.Limits(max_keepalive_connections=5)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True
    )
    async def get_exchange_rate(self, base_currency: str, target_currency: str) -> Optional[float]:
        """
        Получение курса обмена валют с retry-логикой
        """
        try:
            if not self.client:
                raise RuntimeError("Client not initialized. Use 'async with' context manager")

            response = await self.client.get(f"/latest/{base_currency}")
            response.raise_for_status()

            data = response.json()
            rates = data.get("rates", {})

            if target_currency in rates:
                return rates[target_currency]
            else:
                logger.error(f"Currency {target_currency} not found in rates")
                return None

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise

    async def convert_currency(
            self, amount: float, from_currency: str, to_currency: str
    ) -> Optional[float]:
        """Конвертация суммы из одной валюты в другую"""
        rate = await self.get_exchange_rate(from_currency, to_currency)
        if rate:
            return round(amount * rate, 2)
        return None


class ReviewsService:
    """Сервис для работы с внешним API отзывов"""

    def __init__(self, base_url: str = "https://api.reviews-service.com"):
        self.base_url = base_url

    async def fetch_reviews(
            self, product_id: int, http_client: httpx.AsyncClient
    ) -> list:
        """
        Получение отзывов о товаре из внешнего API
        """
        try:
            response = await http_client.get(
                f"{self.base_url}/products/{product_id}/reviews",
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch reviews for product {product_id}: {str(e)}")
            return []

    async def post_review(
            self, product_id: int, review_data: dict, http_client: httpx.AsyncClient
    ) -> Optional[dict]:
        """Отправка отзыва во внешний API"""
        try:
            response = await http_client.post(
                f"{self.base_url}/products/{product_id}/reviews",
                json=review_data,
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to post review: {str(e)}")
            return None


# Глобальные инстансы сервисов
exchange_client = ExchangeRatesClient()
reviews_service = ReviewsService()