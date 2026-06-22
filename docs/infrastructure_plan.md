# Инфраструктура SFMShop

## Компоненты

- FastAPI — веб-фреймворк
- PostgreSQL — основная БД
- Redis — кэш
- Docker — контейнеризация
- Kubernetes — оркестрация

## Окружения

dev: локальная БД, 1 реплика
staging: PostgreSQL + Redis, 2 реплики
production: PostgreSQL + Redis, 3-10 реплик (HPA)

## Мониторинг

- Логирование: LogService (файл + консоль)
- Ошибки: Sentry (опционально)
- Метрики: RPS, latency через логи