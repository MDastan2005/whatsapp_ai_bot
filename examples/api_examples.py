import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

"""
API Examples for WhatsApp FAQ Bot
Примеры использования API WhatsApp FAQ бота
"""

import requests
import json
from typing import Dict, Any


class WhatsAppBotAPI:
    """Клиент для работы с API WhatsApp FAQ бота"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
    
    def health_check(self) -> Dict[str, Any]:
        """Проверка состояния сервиса"""
        response = requests.get(f"{self.base_url}/")
        return response.json()
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики бота"""
        response = requests.get(f"{self.base_url}/stats")
        return response.json()
    
    def reload_faq(self) -> Dict[str, Any]:
        """Перезагрузка базы FAQ"""
        response = requests.post(f"{self.base_url}/reload-faq")
        return response.json()
    
    def simulate_webhook(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Симуляция webhook сообщения (для тестирования)"""
        response = requests.post(
            f"{self.base_url}/webhook",
            json=message_data,
            headers={'Content-Type': 'application/json'}
        )
        return response.json()


def example_health_check():
    """Пример проверки состояния сервиса"""
    print("=== Проверка состояния сервиса ===")
    
    api = WhatsAppBotAPI()
    try:
        result = api.health_check()
        print(f"Статус: {result.get('status')}")
        print(f"Сервис: {result.get('service')}")
        print(f"Время: {result.get('timestamp')}")
        
        if 'bot_stats' in result:
            stats = result['bot_stats']
            print(f"Пользователей: {stats.get('total_users', 0)}")
            print(f"Сообщений: {stats.get('total_messages', 0)}")
            
    except requests.exceptions.RequestException as e:
        print(f"Ошибка подключения: {e}")


def example_get_stats():
    """Пример получения статистики"""
    print("\n=== Получение статистики ===")
    
    api = WhatsAppBotAPI()
    try:
        result = api.get_stats()
        print(f"Всего пользователей: {result.get('total_users', 0)}")
        print(f"Всего сообщений: {result.get('total_messages', 0)}")
        print(f"Среднее сообщений на пользователя: {result.get('average_messages_per_user', 0)}")
        print(f"FAQ записей: {result.get('faq_items', 0)}")
        
    except requests.exceptions.RequestException as e:
        print(f"Ошибка подключения: {e}")


def example_reload_faq():
    """Пример перезагрузки FAQ"""
    print("\n=== Перезагрузка FAQ ===")
    
    api = WhatsAppBotAPI()
    try:
        result = api.reload_faq()
        if result.get('status') == 'success':
            print("✅ FAQ успешно перезагружен")
        else:
            print(f"❌ Ошибка: {result.get('error', 'Неизвестная ошибка')}")
            
    except requests.exceptions.RequestException as e:
        print(f"Ошибка подключения: {e}")


def example_simulate_message():
    """Пример симуляции сообщения"""
    print("\n=== Симуляция сообщения ===")
    
    # Создаем тестовые данные webhook
    webhook_data = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "id": "test_message_id_123",
                        "from": "79123456789",
                        "timestamp": "1234567890",
                        "type": "text",
                        "text": {
                            "body": "Как оформить заказ?"
                        }
                    }],
                    "contacts": [{
                        "profile": {
                            "name": "Тестовый пользователь"
                        }
                    }]
                }
            }]
        }]
    }
    
    api = WhatsAppBotAPI()
    try:
        result = api.simulate_webhook(webhook_data)
        print(f"Результат обработки: {result.get('status')}")
        
    except requests.exceptions.RequestException as e:
        print(f"Ошибка подключения: {e}")


def example_curl_commands():
    """Примеры curl команд для тестирования API"""
    print("\n=== Примеры curl команд ===")
    
    base_url = "http://localhost:5000"
    
    commands = [
        f"# Проверка состояния сервиса\ncurl -X GET {base_url}/",
        
        f"# Получение статистики\ncurl -X GET {base_url}/stats",
        
        f"# Перезагрузка FAQ\ncurl -X POST {base_url}/reload-faq",
        
        f"""# Симуляция webhook сообщения
curl -X POST {base_url}/webhook \\
  -H "Content-Type: application/json" \\
  -d '{{"entry":[{{"changes":[{{"value":{{"messages":[{{"id":"test","from":"79123456789","timestamp":"1234567890","type":"text","text":{{"body":"Привет"}}}}],"contacts":[{{"profile":{{"name":"Тест"}}}}]}}}}]}}]}}'"""
    ]
    
    for command in commands:
        print(command)
        print()


def example_webhook_verification():
    """Пример верификации webhook"""
    print("\n=== Верификация webhook ===")
    
    # Параметры для верификации (замените на ваши)
    verify_token = "your_webhook_verify_token"
    challenge = "test_challenge_string"
    
    url = f"http://localhost:5000/webhook?hub.mode=subscribe&hub.verify_token={verify_token}&hub.challenge={challenge}"
    
    print(f"URL для верификации: {url}")
    print(f"curl -X GET '{url}'")


if __name__ == "__main__":
    print("🤖 WhatsApp FAQ Bot - Примеры использования API")
    print("=" * 50)
    
    # Запускаем примеры
    example_health_check()
    example_get_stats()
    example_reload_faq()
    example_simulate_message()
    example_curl_commands()
    example_webhook_verification()
    
    print("\n=== Интерактивный тест бота ===")
    print("Введите вопрос (или 'exit' для выхода):")
    from app.bot import WhatsAppBot
    bot = WhatsAppBot()
    while True:
        user_question = input("Вы: ")
        if user_question.lower() in ("exit", "quit"): break
        response = bot._process_user_message("79991234567", user_question, "Тестовый Пользователь")
        print("Бот:", response)
    
    print("\n" + "=" * 50)
    print("✅ Примеры завершены")
    print("\n💡 Для запуска бота выполните: python main.py")
    print("💡 Убедитесь, что сервер запущен перед тестированием API") 