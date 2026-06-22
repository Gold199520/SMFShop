# SFMShop - Интернет-магазин

Продвинутое FastAPI приложение с PostgreSQL, Redis, JWT и микросервисной архитектурой.

## Стек

- **Backend:** FastAPI, Python 3.14
- **БД:** PostgreSQL (asyncpg)
- **Кэш:** Redis
- **Auth:** JWT
- **Тесты:** pytest, pytest-cov

## Установка

python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt

## Запуск

uvicorn src.api.main:app --reload

## Тесты

PYTHONPATH=. pytest tests/ -v
PYTHONPATH=. pytest --cov=src --cov-report=term-missing