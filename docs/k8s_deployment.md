# Развертывание SFMShop в Kubernetes

## Обзор

Проект SFMShop развертывается в Kubernetes с использованием Deployment и Service.

## Компоненты

- **Deployment:** 3 реплики приложения с автоматическим восстановлением
- **Service:** LoadBalancer для внешнего доступа
- **Probes:** liveness и readiness для проверки здоровья

## Развертывание

kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
## Проверка статуса
kubectl get pods
kubectl get services
kubectl get deployments
## Масштабирование
kubectl scale deployment sfmshop-deployment --replicas=5
kubectl logs -f deployment/sfmshop-deployment
## Откат обновления
kubectl rollout undo deployment/sfmshop-deployment
