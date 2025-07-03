"""
Tests for WhatsApp FAQ Bot
Тесты для WhatsApp FAQ бота
"""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import openai

# Импортируем модули для тестирования
from app.bot import WhatsAppBot
from app.faq_manager import FAQManager
from app.openai_client import OpenAIClient
from app.whatsapp_client import WhatsAppClient
from config import Config


class TestFAQManager:
    """Тесты для FAQ менеджера"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        # Создаем временный файл для тестов
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file_path = self.temp_file.name
        
        # Тестовые данные FAQ
        test_faq = {
            "faq": [
                {
                    "id": 1,
                    "question": "Как оформить заказ?",
                    "answer": "Для оформления заказа свяжитесь с менеджером",
                    "keywords": ["заказ", "оформить"]
                },
                {
                    "id": 2,
                    "question": "Какие способы оплаты?",
                    "answer": "Мы принимаем карты и наличные",
                    "keywords": ["оплата", "карта"]
                }
            ]
        }
        
        json.dump(test_faq, self.temp_file, ensure_ascii=False, indent=2)
        self.temp_file.close()
        
        # Создаем FAQ менеджер с тестовым файлом
        with patch.object(Config, 'FAQ_FILE_PATH', self.temp_file_path):
            self.faq_manager = FAQManager()
    
    def teardown_method(self):
        """Очистка после каждого теста"""
        if os.path.exists(self.temp_file_path):
            os.unlink(self.temp_file_path)
    
    def test_load_faq(self):
        """Тест загрузки FAQ"""
        assert len(self.faq_manager.faq_data) == 2
        assert self.faq_manager.faq_data[0]['question'] == "Как оформить заказ?"
    
    def test_search_faq(self):
        """Тест поиска FAQ"""
        results = self.faq_manager.search_faq("заказ")
        assert len(results) > 0
        assert results[0]['id'] == 1
    
    def test_search_faq_no_results(self):
        """Тест поиска FAQ без результатов"""
        results = self.faq_manager.search_faq("несуществующий запрос")
        assert len(results) == 0
    
    def test_add_faq_item(self):
        """Тест добавления FAQ записи"""
        success = self.faq_manager.add_faq_item(
            "Новый вопрос?",
            "Новый ответ",
            ["новый", "вопрос"]
        )
        assert success
        assert len(self.faq_manager.faq_data) == 3
    
    def test_get_faq_stats(self):
        """Тест получения статистики FAQ"""
        stats = self.faq_manager.get_faq_stats()
        assert stats['total_items'] == 2
        assert stats['total_keywords'] == 4


class TestOpenAIClient:
    """Тесты для OpenAI клиента"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        with patch.object(Config, 'OPENAI_API_KEY', 'test_key'):
            self.openai_client = OpenAIClient()
    
    @patch('openai.chat.completions.create')
    def test_generate_faq_response(self, mock_create):
        """Тест генерации ответа на основе FAQ"""
        mock_response = Mock()
        mock_choice = Mock()
        mock_choice.message = Mock()
        mock_choice.message.content = "Тестовый ответ"
        mock_response.choices = [mock_choice]
        mock_create.return_value = mock_response
        faq_context = [{"question": "Тест?", "answer": "Тестовый ответ"}]
        result = self.openai_client.generate_faq_response("Тестовый вопрос", faq_context)
        assert result == "Тестовый ответ"
    
    @patch('openai.chat.completions.create')
    def test_classify_intent(self, mock_create):
        """Тест классификации намерения"""
        mock_response = Mock()
        mock_choice = Mock()
        mock_choice.message = Mock()
        mock_choice.message.content = "question"
        mock_response.choices = [mock_choice]
        mock_create.return_value = mock_response
        intent = self.openai_client.classify_intent("Как оформить заказ?")
        assert intent == "question"


class TestWhatsAppClient:
    """Тесты для WhatsApp клиента"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        with patch.object(Config, 'WHATSAPP_TOKEN', 'test_token'), \
             patch.object(Config, 'WHATSAPP_PHONE_NUMBER_ID', 'test_phone_id'):
            self.whatsapp_client = WhatsAppClient()
    
    def test_extract_message_data_valid(self):
        """Тест извлечения данных сообщения из валидного webhook"""
        webhook_data = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "id": "test_id",
                            "from": "1234567890",
                            "timestamp": "1234567890",
                            "type": "text",
                            "text": {"body": "Тестовое сообщение"}
                        }],
                        "contacts": [{
                            "profile": {"name": "Тестовый пользователь"}
                        }]
                    }
                }]
            }]
        }
        
        result = self.whatsapp_client.extract_message_data(webhook_data)
        
        assert result is not None
        assert result['message_id'] == "test_id"
        assert result['from'] == "1234567890"
        assert result['text'] == "Тестовое сообщение"
        assert result['contact_name'] == "Тестовый пользователь"
    
    def test_extract_message_data_invalid(self):
        """Тест извлечения данных из невалидного webhook"""
        webhook_data = {"invalid": "data"}
        result = self.whatsapp_client.extract_message_data(webhook_data)
        assert result is None
    
    @patch('requests.post')
    def test_send_text_message_success(self, mock_post):
        """Тест успешной отправки текстового сообщения"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = self.whatsapp_client.send_text_message("1234567890", "Тестовое сообщение")
        assert result is True
    
    @patch('requests.post')
    def test_send_text_message_failure(self, mock_post):
        """Тест неудачной отправки текстового сообщения"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Error"
        mock_post.return_value = mock_response
        
        result = self.whatsapp_client.send_text_message("1234567890", "Тестовое сообщение")
        assert result is False


class TestWhatsAppBot:
    """Тесты для основного бота"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        # Мокаем все зависимости
        with patch('app.bot.WhatsAppClient'), \
             patch('app.bot.OpenAIClient'), \
             patch('app.bot.FAQManager'):
            self.bot = WhatsAppBot()
    
    def test_get_user_session_new(self):
        """Тест создания новой сессии пользователя"""
        session = self.bot._get_user_session("1234567890")
        assert session['greeted'] is False
        assert session['message_count'] == 0
        assert "1234567890" in self.bot.user_sessions
    
    def test_get_user_session_existing(self):
        """Тест получения существующей сессии пользователя"""
        # Создаем сессию
        session1 = self.bot._get_user_session("1234567890")
        session1['greeted'] = True
        session1['message_count'] = 5
        
        # Получаем ту же сессию
        session2 = self.bot._get_user_session("1234567890")
        assert session2['greeted'] is True
        assert session2['message_count'] == 5
    
    def test_get_fallback_response(self):
        """Тест резервного ответа"""
        response = self.bot._get_fallback_response()
        assert "не нашел" in response.lower()
        assert "менеджер" in response.lower()
    
    def test_get_general_help_response(self):
        """Тест общего ответа помощи"""
        response = self.bot._get_general_help_response()
        assert "бот-помощник" in response.lower()
        assert "помочь" in response.lower()
    
    def test_get_error_response(self):
        """Тест ответа при ошибке"""
        response = self.bot._get_error_response()
        assert "техническая ошибка" in response.lower()
        assert "извинения" in response.lower()
    
    def test_get_bot_stats(self):
        """Тест получения статистики бота"""
        # Добавляем тестовые сессии
        self.bot.user_sessions["123"] = {"message_count": 5}
        self.bot.user_sessions["456"] = {"message_count": 3}
        
        # Мокаем FAQ статистику
        self.bot.faq.get_faq_stats = Mock(return_value={"total_items": 10})
        
        stats = self.bot.get_bot_stats()
        
        assert stats['total_users'] == 2
        assert stats['total_messages'] == 8
        assert stats['average_messages_per_user'] == 4.0
        assert stats['faq_items'] == 10


class TestConfig:
    """Тесты для конфигурации"""
    
    def test_validate_config_missing_vars(self):
        """Тест валидации конфигурации с отсутствующими переменными"""
        with patch.object(Config, 'WHATSAPP_TOKEN', None):
            with pytest.raises(ValueError) as exc_info:
                Config.validate_config()
            assert "WHATSAPP_TOKEN" in str(exc_info.value)
    
    def test_get_config_dict(self):
        """Тест получения конфигурации в виде словаря"""
        config_dict = Config.get_config_dict()
        
        assert 'flask_port' in config_dict
        assert 'flask_debug' in config_dict
        assert 'log_level' in config_dict
        assert 'faq_file_path' in config_dict
        
        # Проверяем, что секретные данные не включены
        assert 'whatsapp_token' not in config_dict
        assert 'openai_api_key' not in config_dict


# Интеграционные тесты
class TestIntegration:
    """Интеграционные тесты"""
    
    @patch('app.bot.WhatsAppClient')
    @patch('app.bot.OpenAIClient')
    @patch('app.bot.FAQManager')
    def test_bot_initialization(self, mock_faq, mock_openai, mock_whatsapp):
        """Тест инициализации бота"""
        bot = WhatsAppBot()
        
        # Проверяем, что все компоненты инициализированы
        assert bot.whatsapp is not None
        assert bot.openai is not None
        assert bot.faq is not None
        assert bot.user_sessions == {}
    
    def test_webhook_message_processing(self):
        """Тест обработки webhook сообщения"""
        # Создаем тестовые данные webhook
        webhook_data = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "id": "test_id",
                            "from": "1234567890",
                            "timestamp": "1234567890",
                            "type": "text",
                            "text": {"body": "Как оформить заказ?"}
                        }],
                        "contacts": [{
                            "profile": {"name": "Тестовый пользователь"}
                        }]
                    }
                }]
            }]
        }
        
        # Мокаем все зависимости
        with patch('app.bot.WhatsAppClient') as mock_whatsapp, \
             patch('app.bot.OpenAIClient') as mock_openai, \
             patch('app.bot.FAQManager') as mock_faq:
            
            bot = WhatsAppBot()
            
            # Настраиваем моки
            mock_whatsapp.return_value.extract_message_data.return_value = {
                'message_id': 'test_id',
                'from': '1234567890',
                'text': 'Как оформить заказ?',
                'type': 'text',
                'contact_name': 'Тестовый пользователь'
            }
            
            mock_whatsapp.return_value.mark_message_as_read.return_value = True
            mock_whatsapp.return_value.send_text_message.return_value = True
            
            mock_openai.return_value.classify_intent.return_value = 'question'
            
            mock_faq.return_value.search_faq.return_value = [
                {'question': 'Как оформить заказ?', 'answer': 'Свяжитесь с менеджером'}
            ]
            
            mock_openai.return_value.generate_faq_response.return_value = "Свяжитесь с менеджером"
            
            # Обрабатываем сообщение
            result = bot.handle_message(webhook_data)
            
            assert result is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
