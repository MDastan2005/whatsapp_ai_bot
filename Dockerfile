# Production-ready Dockerfile for WhatsApp FAQ Bot
FROM python:3.9-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Создание пользователя для безопасности
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Открытие порта
EXPOSE 5000

# Запуск приложения через gunicorn (production)
CMD ["gunicorn", "main:app", "-b", "0.0.0.0:5000", "--timeout", "120"] 