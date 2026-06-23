import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from src.services.cache_service import CacheService

@pytest.fixture
def mock_redis():
    return AsyncMock()

@pytest.fixture
def cache(mock_redis):
    return CacheService(mock_redis)

@pytest.mark.asyncio
async def test_get_cached_value(cache, mock_redis):
    mock_redis.get.return_value = json.dumps({"test": "data"})
    result = await cache.get("test_key")
    assert result == {"test": "data"}
    mock_redis.get.assert_called_once_with("test_key")

@pytest.mark.asyncio
async def test_get_cache_miss(cache, mock_redis):
    mock_redis.get.return_value = None
    result = await cache.get("missing_key")
    assert result is None

@pytest.mark.asyncio
async def test_get_no_redis():
    cache = CacheService(None)
    result = await cache.get("key")
    assert result is None

@pytest.mark.asyncio
async def test_set_cache(cache, mock_redis):
    result = await cache.set("key", {"data": 123}, ttl=600)
    assert result == True
    mock_redis.setex.assert_called_once()

@pytest.mark.asyncio
async def test_set_no_redis():
    cache = CacheService(None)
    result = await cache.set("key", "value")
    assert result == False

@pytest.mark.asyncio
async def test_delete_cache(cache, mock_redis):
    await cache.delete("key")
    mock_redis.delete.assert_called_once_with("key")

@pytest.mark.asyncio
async def test_delete_no_redis():
    cache = CacheService(None)
    result = await cache.delete("key")
    assert result == False

@pytest.mark.asyncio
async def test_clear_pattern(cache, mock_redis):
    mock_redis.keys.return_value = ["key1", "key2"]
    mock_redis.delete.return_value = 2
    result = await cache.clear_pattern("test:*")
    assert result == 2

@pytest.mark.asyncio
async def test_clear_pattern_empty(cache, mock_redis):
    mock_redis.keys.return_value = []
    result = await cache.clear_pattern("none:*")
    assert result == 0

@pytest.mark.asyncio
async def test_clear_pattern_no_redis():
    cache = CacheService(None)
    result = await cache.clear_pattern("pattern")
    assert result == 0
