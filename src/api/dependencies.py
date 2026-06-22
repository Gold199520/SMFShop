from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import asyncpg
import redis.asyncio as aioredis
from typing import Optional
import jwt
from jwt.exceptions import PyJWTError
import os
from dotenv import load_dotenv

load_dotenv()

security = HTTPBearer()

# Конфигурация базы данных
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/sfmshop")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"


# Подключение к PostgreSQL
async def get_db():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        await conn.close()


# Подключение к Redis
async def get_redis():
    try:
        redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)
        yield redis_client
        await redis_client.close()
    except Exception as e:
        # Если Redis недоступен, продолжаем без кэширования
        yield None


# Аутентификация через JWT
async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: asyncpg.Connection = Depends(get_db)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )

    # Проверяем существование пользователя в БД
    user = await db.fetchrow("SELECT id, username, email FROM users WHERE id = $1", user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return dict(user)


# Опциональная аутентификация (для публичных endpoint'ов)
async def get_optional_user(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[dict]:
    if not credentials:
        return None

    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {"user_id": payload.get("sub")}
    except:
        return None