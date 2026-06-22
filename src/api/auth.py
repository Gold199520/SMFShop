from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta
import jwt
import asyncpg
from passlib.context import CryptContext
import os
from src.api.schemas import UserCreate, UserLogin, TokenResponse
from src.api.dependencies import get_db, JWT_SECRET, JWT_ALGORITHM

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(user_id: int) -> str:
    """Создание JWT токена"""
    expire = datetime.utcnow() + timedelta(hours=24)
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db: asyncpg.Connection = Depends(get_db)):
    """Регистрация нового пользователя"""

    # Проверяем, существует ли пользователь
    existing = await db.fetchrow(
        "SELECT id FROM users WHERE username = $1 OR email = $2",
        user_data.username, user_data.email
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким username или email уже существует"
        )

    # Хешируем пароль
    hashed_password = pwd_context.hash(user_data.password)

    # Создаем пользователя
    user = await db.fetchrow(
        """
        INSERT INTO users (username, email, password_hash)
        VALUES ($1, $2, $3)
        RETURNING id, username, email
        """,
        user_data.username, user_data.email, hashed_password
    )

    # Создаем токен
    token = create_access_token(user['id'])

    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: asyncpg.Connection = Depends(get_db)):
    """Вход пользователя"""

    # Ищем пользователя
    user = await db.fetchrow(
        "SELECT id, username, password_hash FROM users WHERE username = $1",
        credentials.username
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль"
        )

    # Проверяем пароль
    if not pwd_context.verify(credentials.password, user['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль"
        )

    # Создаем токен
    token = create_access_token(user['id'])

    return TokenResponse(access_token=token)