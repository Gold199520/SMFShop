import httpx
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
import asyncpg
from typing import List, Optional
import asyncio
import logging

from src.api.schemas import ProductCreate, ProductUpdate, ProductResponse
from src.api.dependencies import get_db, get_redis, get_current_user
from src.services.cache_service import CacheService
from src.services.external_api_service import reviews_service

router = APIRouter(prefix="/products", tags=["Products"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[ProductResponse])
async def get_products(
        page: int = Query(1, ge=1),
        limit: int = Query(20, ge=1, le=100),
        category: Optional[str] = None,
        db: asyncpg.Connection = Depends(get_db),
        redis_client=Depends(get_redis),
        current_user: dict = Depends(get_current_user)
):
    """Получение списка товаров с пагинацией и фильтрацией"""

    # Проверяем кэш
    cache_service = CacheService(redis_client)
    cache_key = f"products:list:{page}:{limit}:{category}"

    cached = await cache_service.get(cache_key)
    if cached:
        return cached

    # Строим запрос
    query = "SELECT * FROM products"
    params = []

    if category:
        query += " WHERE category = $1"
        params.append(category)

    # Считаем общее количество
    count_query = query.replace("SELECT *", "SELECT COUNT(*)")
    total = await db.fetchval(count_query, *params)

    # Добавляем пагинацию
    offset = (page - 1) * limit
    query += f" ORDER BY created_at DESC LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}"
    params.extend([limit, offset])

    products = await db.fetch(query, *params)
    result = [dict(p) for p in products]

    # Сохраняем в кэш на 5 минут
    await cache_service.set(cache_key, result, ttl=300)

    return result


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
        product_id: int,
        db: asyncpg.Connection = Depends(get_db),
        redis_client=Depends(get_redis),
        current_user: dict = Depends(get_current_user)
):
    """Получение информации о конкретном товаре"""

    cache_service = CacheService(redis_client)
    cache_key = f"product:{product_id}"

    # Проверяем кэш
    cached = await cache_service.get(cache_key)
    if cached:
        return cached

    product = await db.fetchrow("SELECT * FROM products WHERE id = $1", product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    result = dict(product)

    # Сохраняем в кэш на 10 минут
    await cache_service.set(cache_key, result, ttl=600)

    return result


@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(
        product_data: ProductCreate,
        background_tasks: BackgroundTasks,
        db: asyncpg.Connection = Depends(get_db),
        redis_client=Depends(get_redis),
        current_user: dict = Depends(get_current_user)
):
    """Создание нового товара"""

    product = await db.fetchrow(
        """
        INSERT INTO products (name, description, price, stock, category)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING *
        """,
        product_data.name, product_data.description,
        product_data.price, product_data.stock, product_data.category
    )

    result = dict(product)

    # Фоновая задача: очистка кэша списка товаров
    background_tasks.add_task(
        CacheService(redis_client).clear_pattern,
        "products:list:*"
    )

    return result


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
        product_id: int,
        product_data: ProductUpdate,
        background_tasks: BackgroundTasks,
        db: asyncpg.Connection = Depends(get_db),
        redis_client=Depends(get_redis),
        current_user: dict = Depends(get_current_user)
):
    """Обновление товара"""

    # Проверяем существование товара
    existing = await db.fetchrow("SELECT * FROM products WHERE id = $1", product_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Товар не найден")

    # Обновляем только предоставленные поля
    updates = {}
    for field, value in product_data.dict(exclude_unset=True).items():
        if value is not None:
            updates[field] = value

    if not updates:
        return dict(existing)

    # Строим динамический UPDATE запрос
    set_clause = ", ".join([f"{k} = ${i + 2}" for i, k in enumerate(updates.keys())])
    values = list(updates.values())

    query = f"""
        UPDATE products 
        SET {set_clause}, updated_at = NOW()
        WHERE id = $1
        RETURNING *
    """

    updated = await db.fetchrow(query, product_id, *values)
    result = dict(updated)

    # Очищаем кэш
    cache_service = CacheService(redis_client)
    background_tasks.add_task(cache_service.delete, f"product:{product_id}")
    background_tasks.add_task(cache_service.clear_pattern, "products:list:*")

    return result


@router.delete("/{product_id}", status_code=204)
async def delete_product(
        product_id: int,
        background_tasks: BackgroundTasks,
        db: asyncpg.Connection = Depends(get_db),
        redis_client=Depends(get_redis),
        current_user: dict = Depends(get_current_user)
):
    """Удаление товара"""

    result = await db.execute("DELETE FROM products WHERE id = $1", product_id)
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Товар не найден")

    # Очищаем кэш
    cache_service = CacheService(redis_client)
    background_tasks.add_task(cache_service.delete, f"product:{product_id}")
    background_tasks.add_task(cache_service.clear_pattern, "products:list:*")


@router.get("/{product_id}/full")
async def get_product_full(
        product_id: int,
        db: asyncpg.Connection = Depends(get_db),
        redis_client=Depends(get_redis),
        current_user: dict = Depends(get_current_user)
):
    """Полная информация о товаре из трёх источников (параллельно)"""

    cache_service = CacheService(redis_client)
    cache_key = f"product:{product_id}:full"

    # Проверяем кэш
    cached = await cache_service.get(cache_key)
    if cached:
        return cached

    # Функции для параллельного выполнения
    async def get_product():
        row = await db.fetchrow("SELECT * FROM products WHERE id = $1", product_id)
        if not row:
            raise HTTPException(status_code=404, detail="Товар не найден")
        return dict(row)

    async def get_views():
        views = await redis_client.get(f"product:{product_id}:views") if redis_client else 0
        return int(views) if views else 0

    async def get_reviews():
        # Пытаемся взять из кэша
        reviews_cache = await cache_service.get(f"product:{product_id}:reviews")
        if reviews_cache is not None:
            return reviews_cache

        # Запрашиваем из внешнего API
        async with httpx.AsyncClient() as client:
            reviews = await reviews_service.fetch_reviews(product_id, client)

            # Кэшируем отзывы на 10 минут
            await cache_service.set(
                f"product:{product_id}:reviews",
                reviews,
                ttl=600
            )

            return reviews

    # Параллельное выполнение
    product_task = get_product()
    views_task = get_views()
    reviews_task = get_reviews()

    product_data, views_count, reviews = await asyncio.gather(
        product_task, views_task, reviews_task
    )

    result = {
        "product": product_data,
        "views_count": views_count,
        "reviews": reviews,
        "exchange_rates": {}
    }

    # Добавляем конвертацию валют (фоновая задача)
    exchange_client = ExchangeRatesClient()
    async with exchange_client as ec:
        try:
            usd_rate = await ec.get_exchange_rate("RUB", "USD")
            eur_rate = await ec.get_exchange_rate("RUB", "EUR")

            if usd_rate:
                result["exchange_rates"]["USD"] = {
                    "rate": usd_rate,
                    "price": round(product_data["price"] * usd_rate, 2)
                }
            if eur_rate:
                result["exchange_rates"]["EUR"] = {
                    "rate": eur_rate,
                    "price": round(product_data["price"] * eur_rate, 2)
                }
        except Exception as e:
            logger.error(f"Failed to get exchange rates: {str(e)}")

    # Кэшируем полный результат на 2 минуты
    await cache_service.set(cache_key, result, ttl=120)

    return result