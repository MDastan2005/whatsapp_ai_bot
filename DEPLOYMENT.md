# 🚀 Инструкции по развертыванию WhatsApp FAQ Bot

## 📋 Содержание

1. [Локальное развертывание](#локальное-развертывание)
2. [Развертывание на сервере](#развертывание-на-сервере)
3. [Docker развертывание](#docker-развертывание)
4. [Настройка WhatsApp Business API](#настройка-whatsapp-business-api)
5. [Мониторинг и логирование](#мониторинг-и-логирование)
6. [Безопасность](#безопасность)

## 🏠 Локальное развертывание

### Требования

- Python 3.8+
- pip
- Git

### Шаги установки

1. **Клонирование репозитория**
```bash
git clone https://github.com/yourusername/whatsapp-faq-bot.git
cd whatsapp-faq-bot
```

2. **Создание виртуального окружения**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
```

3. **Установка зависимостей**
```bash
pip install -r requirements.txt
```

4. **Настройка переменных окружения**
```bash
cp .env.example .env
# Отредактируйте .env файл с вашими API ключами
```

5. **Запуск приложения**
```bash
python main.py
```

Сервер запустится на `http://localhost:5000`

## 🌐 Развертывание на сервере

### Подготовка сервера

1. **Обновление системы**
```bash
sudo apt update && sudo apt upgrade -y
```

2. **Установка Python и зависимостей**
```bash
sudo apt install python3 python3-pip python3-venv nginx supervisor -y
```

3. **Создание пользователя для приложения**
```bash
sudo adduser whatsapp-bot
sudo usermod -aG sudo whatsapp-bot
```

### Установка приложения

1. **Клонирование и настройка**
```bash
sudo -u whatsapp-bot git clone https://github.com/yourusername/whatsapp-faq-bot.git /home/whatsapp-bot/app
cd /home/whatsapp-bot/app

sudo -u whatsapp-bot python3 -m venv venv
sudo -u whatsapp-bot venv/bin/pip install -r requirements.txt
```

2. **Настройка переменных окружения**
```bash
sudo -u whatsapp-bot cp .env.example .env
sudo nano .env  # Настройте API ключи
```

3. **Настройка Supervisor**
```bash
sudo nano /etc/supervisor/conf.d/whatsapp-bot.conf
```

Содержимое файла:
```ini
[program:whatsapp-bot]
command=/home/whatsapp-bot/app/venv/bin/python /home/whatsapp-bot/app/main.py
directory=/home/whatsapp-bot/app
user=whatsapp-bot
autostart=true
autorestart=true
stderr_logfile=/var/log/whatsapp-bot.err.log
stdout_logfile=/var/log/whatsapp-bot.out.log
environment=FLASK_ENV="production"
```

4. **Запуск через Supervisor**
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start whatsapp-bot
```

### Настройка Nginx

1. **Создание конфигурации**
```bash
sudo nano /etc/nginx/sites-available/whatsapp-bot
```

Содержимое файла:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

2. **Активация сайта**
```bash
sudo ln -s /etc/nginx/sites-available/whatsapp-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🐳 Docker развертывание

### Создание Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Создание пользователя
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Открытие порта
EXPOSE 5000

# Запуск приложения
CMD ["python", "main.py"]
```

### Docker Compose

Создайте `docker-compose.yml`:

```yaml
version: '3.8'

services:
  whatsapp-bot:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - whatsapp-bot
    restart: unless-stopped
```

### Запуск с Docker

```bash
# Сборка и запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f whatsapp-bot

# Остановка
docker-compose down
```

## 📱 Настройка WhatsApp Business API

### 1. Создание Facebook App

1. Перейдите на [Facebook Developers](https://developers.facebook.com/)
2. Создайте новое приложение
3. Добавьте продукт "WhatsApp Business API"

### 2. Настройка WhatsApp Business

1. В настройках WhatsApp Business:
   - Получите `Phone Number ID`
   - Получите `Access Token`
   - Настройте webhook URL

2. Webhook URL должен быть: `https://your-domain.com/webhook`

### 3. Настройка Webhook

1. **Verify Token**: Установите уникальный токен в настройках
2. **Events**: Подпишитесь на события `messages`
3. **Fields**: Выберите поля `messages`, `contacts`

### 4. Тестирование

```bash
# Проверка webhook
curl -X GET "https://your-domain.com/webhook?hub.mode=subscribe&hub.verify_token=YOUR_TOKEN&hub.challenge=test"

# Проверка состояния
curl -X GET "https://your-domain.com/"
```

## 📊 Мониторинг и логирование

### Логирование

Логи сохраняются в папке `logs/` с ротацией по дням.

### Мониторинг через API

```bash
# Статистика бота
curl -X GET "https://your-domain.com/stats"

# Проверка состояния
curl -X GET "https://your-domain.com/"
```

### Настройка мониторинга

1. **Prometheus метрики** (опционально)
2. **Grafana дашборды**
3. **Алерты при ошибках**

## 🔒 Безопасность

### Рекомендации

1. **HTTPS**: Обязательно используйте SSL/TLS
2. **Firewall**: Ограничьте доступ к портам
3. **API ключи**: Храните в безопасном месте
4. **Логи**: Не логируйте чувствительные данные
5. **Обновления**: Регулярно обновляйте зависимости

### Настройка SSL

```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d your-domain.com

# Автоматическое обновление
sudo crontab -e
# Добавьте: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Firewall настройки

```bash
# UFW настройки
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## 🚨 Устранение неполадок

### Частые проблемы

1. **Ошибка подключения к WhatsApp API**
   - Проверьте токен и Phone Number ID
   - Убедитесь в правильности webhook URL

2. **Ошибки OpenAI API**
   - Проверьте API ключ
   - Убедитесь в достаточности кредитов

3. **Проблемы с логированием**
   - Проверьте права доступа к папке logs/
   - Убедитесь в наличии места на диске

### Команды диагностики

```bash
# Проверка состояния сервиса
sudo supervisorctl status whatsapp-bot

# Просмотр логов
tail -f /var/log/whatsapp-bot.out.log
tail -f /var/log/whatsapp-bot.err.log

# Проверка портов
netstat -tlnp | grep :5000

# Тест API
curl -X GET "http://localhost:5000/"
```

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи в папке `logs/`
2. Убедитесь в правильности конфигурации
3. Проверьте статус всех сервисов
4. Создайте Issue в GitHub с подробным описанием

---

**Удачного развертывания! 🚀** 