# Instrumented Weather Service

Демо-приложение для воркшопа по мониторингу в рамках ШИФТ Интенсив 2026.

## Адреса

1. [Спецификация АПИ для FastAPI-приложения](http://localhost:38080/docs)
2. [Web-интерфейс Prometheus](http://localhost:39090)
3. [Web-интерфейс Grafana](http://localhost:33000)

## Сборка Docker Images для проекта

```bash
docker compose -f docker-compose.yaml -f docker-compose-test.yaml build
```

## Запуск приложения

```bash
docker compose up
```

## Запуск тестов

### Без оценки покрытия

```bash
docker compose -f docker-compose-test.yaml run --rm test
```

### С оценкой покрытия

```bash
docker compose -f docker-compose-test.yaml run --rm test-cov
```

## Очистка артефактов в Docker

```bash
docker compose -f docker-compose.yaml -f docker-compose-test.yaml down --rmi all
```
