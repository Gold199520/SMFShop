# SMFShop - Интернет-магазин

Backend интернет-магазина на FastAPI с асинхронной обработкой, микросервисной архитектурой и полным CI/CD пайплайном.

## Стек

Backend: FastAPI, Python 3.14, asyncio
База данных: PostgreSQL (asyncpg), SQLAlchemy 2.0
Кэш и очереди: Redis
Auth: JWT токены
Тесты: pytest, pytest-asyncio, coverage
Инфраструктура: Docker, Docker Compose, Kubernetes
CI/CD: GitHub Actions

## Что реализовано

- REST API для каталога товаров, корзины, заказов и админ панели
- Асинхронная работа с PostgreSQL через SQLAlchemy 2.0 и asyncpg
- JWT авторизация с refresh токенами и ролевой моделью
- Кэширование через Redis для снижения нагрузки на БД
- Обработка фоновых задач
- Покрытие тестами ключевых сценариев
- Контейнеризация через Docker Compose
- Манифесты Kubernetes для продакшен развёртывания
- CI пайплайн на GitHub Actions (lint, tests, build)

## Оптимизации

- Устранил проблему N+1 запросов через selectinload и joinedload
- Добавил индексы в PostgreSQL для частых выборок, ответ API ускорился в 3 раза
- Внедрил кэш Redis для hot данных
- Настроил connection pool для эффективной работы с БД

## Структура проекта

src/
  api/ - роутеры FastAPI
  models/ - SQLAlchemy модели
  schemas/ - Pydantic схемы
  services/ - бизнес логика
  core/ - конфиг, безопасность
tests/ - unit и integration тесты
docker/ - Dockerfile и compose
k8s/ - манифесты Kubernetes
.github/ - CI/CD workflows

## Установка локально

git clone https://github.com/Gold199520/SMFShop.git
cd SMFShop

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

## Запуск через Docker Compose

docker compose up -d

API будет доступен на http://localhost:8000
Документация Swagger: http://localhost:8000/docs

## Запуск без Docker

uvicorn src.api.main:app --reload

## Тесты

PYTHONPATH=. pytest tests/ -v
PYTHONPATH=. pytest --cov=src --cov-report=term-missing

## Переменные окружения

Смотри .env.example для полного списка.

DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/smfshop
REDIS_URL=redis://localhost:6379
JWT_SECRET=your_secret_key
JWT_ALGORITHM=HS256

## Дальнейшие планы

- Добавить Elasticsearch для поиска по каталогу
- Перевести обработку заказов на Kafka для асинхронной интеграции с внешними системами
- Добавить observability через Prometheus и Grafana