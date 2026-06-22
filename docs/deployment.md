# Развертывание SFMShop

## Локальный запуск

python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
uvicorn src.api.main:app --reload

## Docker Compose

cd docker
docker compose up -d

Сервисы: app (8000), PostgreSQL (5432), Redis (6379).

## Kubernetes

kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl scale deployment sfmshop-deployment --replicas=5

## CI/CD

При push в main/develop автоматически запускаются тесты.
При merge в main — деплой.