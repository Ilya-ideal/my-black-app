# My Black App - CI/CD Demo

Простое приложение с черным фоном для демонстрации CI/CD пайплайна.

## Технологии:
- Python/Flask
- Docker
- Kubernetes
- Jenkins
- GitHub Webhooks
- Telegram Notifications

## CI/CD Пайплайн:
1. Push в GitHub → вебхук
2. Jenkins автоматически запускает сборку
3. Собирается Docker образ
4. Образ пушится в Docker Hub
5. Приложение развертывается в Kubernetes
6. Отправляется уведомление в Telegram

## Локальный запуск:
```bash
docker build -t my-black-app .
docker run -p 5000:5000 my-black-app