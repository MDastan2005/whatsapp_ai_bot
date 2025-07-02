# WhatsApp FAQ Bot with OpenAI Integration

## 📋 Описание

WhatsApp бот для автоматических ответов на часто задаваемые вопросы с использованием OpenAI API. Бот загружает базу FAQ из JSON файла и использует GPT для генерации контекстных ответов.

## 🚀 Возможности

- ✅ Интеграция с WhatsApp Business API
- ✅ Автоматические ответы на FAQ
- ✅ Использование OpenAI GPT для умных ответов
- ✅ Загрузка FAQ из JSON файла
- ✅ Логирование всех операций
- ✅ Веб-хук для получения сообщений
- ✅ Поиск по ключевым словам в FAQ

## 📁 Структура проекта

```
whatsapp-faq-bot/
├── app/
│   ├── __init__.py
│   ├── bot.py              # Основная логика бота
│   ├── whatsapp_client.py  # WhatsApp API клиент
│   ├── openai_client.py    # OpenAI API клиент
│   └── faq_manager.py      # Управление FAQ
├── data/
│   └── faq.json           # База частых вопросов
├── logs/
│   └── .gitkeep
├── tests/
│   ├── __init__.py
│   └── test_bot.py
├── .env.example
├── .gitignore
├── requirements.txt
├── main.py
├── config.py
└── README.md
```

## 🛠 Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/whatsapp-faq-bot.git
cd whatsapp-faq-bot
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Настройте переменные окружения:
```bash
cp .env.example .env
# Отредактируйте .env файл с вашими API ключами
```

## ⚙️ Конфигурация

Создайте `.env` файл на основе `.env.example`:

```env
# WhatsApp Business API
WHATSAPP_TOKEN=your_whatsapp_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WEBHOOK_VERIFY_TOKEN=your_webhook_verify_token

# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# Flask настройки
FLASK_PORT=5000
FLASK_DEBUG=True

# Логирование
LOG_LEVEL=INFO
```

## 🏃‍♂️ Запуск

```bash
python main.py
```

Сервер запустится на `http://localhost:5000`

## 📱 Настройка WhatsApp Webhook

1. В Facebook Developers настройте webhook URL: `https://yourdomain.com/webhook`
2. Установите Verify Token из вашего `.env` файла
3. Подпишитесь на события `messages`

## 📚 Добавление FAQ

Отредактируйте файл `data/faq.json`:

```json
{
  "faq": [
    {
      "id": 1,
      "question": "Как оформить заказ?",
      "answer": "Для оформления заказа...",
      "keywords": ["заказ", "оформить", "купить"]
    },
    {
      "id": 2,
      "question": "Какие способы оплаты?",
      "answer": "Мы принимаем...",
      "keywords": ["оплата", "способы", "платить"]
    }
  ]
}
```

## 🧪 Тестирование

```bash
python -m pytest tests/
```

## 📋 API Endpoints

- `GET /` - Статус бота
- `GET /webhook` - Верификация webhook
- `POST /webhook` - Получение WhatsApp сообщений

## 📊 Логи

Все логи сохраняются в папке `logs/` с ротацией по дням.

## 🔒 Безопасность

- Все API ключи хранятся в переменных окружения
- Webhook токен проверяется для безопасности
- Логирование не содержит чувствительных данных

## 🤝 Вклад в проект

1. Fork проекта
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

MIT License - смотрите [LICENSE](LICENSE) файл для деталей.

## 📞 Поддержка

Если у вас есть вопросы, создайте [Issue](https://github.com/yourusername/whatsapp-faq-bot/issues) в GitHub.

---

**Разработано с Салаватом и Дастаном для автоматизации клиентской поддержки**