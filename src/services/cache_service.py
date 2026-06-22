import json
import logging
from typing import Optional, Any
import redis.asyncio as aioredis
from functools import wraps

logger = logging.getLogger(__name__)


class CacheService:
    """Сервис для работы с кэшем Redis"""

    def __init__(self, redis_client: Optional[aioredis.Redis] = None):
        self.redis = redis_client
        self.default_ttl = 3600  # 1 час по умолчанию

    async def get(self, key: str) -> Optional[Any]:
        """Получение значения из кэша"""
        if not self.redis:
            return None

        try:
            cached = await self.redis.get(key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.error(f"Redis get error for key {key}: {str(e)}")
        return None

    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Сохранение значения в кэш"""
        if not self.redis:
            return False

        ttl = ttl or self.default_ttl

        try:
            serialized = json.dumps(value, default=str)
            await self.redis.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Redis set error for key {key}: {str(e)}")
            return False

    async def delete(self, key: str) -> bool:
        """Удаление значения из кэша"""
        if not self.redis:
            return False

        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis delete error for key {key}: {str(e)}")
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """Удаление всех ключей по паттерну"""
        if not self.redis:
            return 0

        try:
            keys = await self.redis.keys(pattern)
            if keys:
                deleted = await self.redis.delete(*keys)
                return deleted
        except Exception as e:
            logger.error(f"Redis clear pattern error: {str(e)}")
        return 0


# Декоратор для кэширования
def cache_response(ttl: int = 3600, key_prefix: str = "cache"):
    """Декоратор для кэширования ответов endpoint'ов"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Извлекаем redis клиент из kwargs
            redis_client = kwargs.get('redis_cache')
            cache_service = CacheService(redis_client)

            # Формируем ключ кэша
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"

            # Проверяем кэш
            cached = await cache_service.get(cache_key)
            if cached is not None:
                logger.info(f"Cache hit for {cache_key}")
                return cached

            # Выполняем функцию
            result = await func(*args, **kwargs)

            # Сохраняем в кэш
            await cache_service.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator