"""
Configuration module for WhatsApp FAQ Bot
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # WhatsApp Business API
    WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
    WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
    WEBHOOK_VERIFY_TOKEN = os.getenv('WEBHOOK_VERIFY_TOKEN')
    
    # OpenAI API
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Flask настройки
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes', 'on')
    
    # Логирование
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Пути к файлам
    FAQ_FILE_PATH = os.getenv('FAQ_FILE_PATH', 'data/faq.json')
    LOG_DIR = os.getenv('LOG_DIR', 'logs')
    
    # OpenAI настройки
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', 500))
    OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', 0.7))
    
    # Лимиты и настройки бота
    MAX_FAQ_RESULTS = int(os.getenv('MAX_FAQ_RESULTS', 3))
    MAX_MESSAGE_LENGTH = int(os.getenv('MAX_MESSAGE_LENGTH', 4096))
    SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 3600))  # в секундах
    
    @classmethod
    def validate_config(cls):
        """Проверяет наличие обязательных переменных окружения"""
        required_vars = [
            'WHATSAPP_TOKEN',
            'WHATSAPP_PHONE_NUMBER_ID', 
            'WEBHOOK_VERIFY_TOKEN',
            'OPENAI_API_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Отсутствуют переменные окружения: {', '.join(missing_vars)}")
        
        return True
    
    @classmethod
    def get_config_dict(cls):
        """Возвращает конфигурацию в виде словаря (без секретных данных)"""
        return {
            'flask_port': cls.FLASK_PORT,
            'flask_debug': cls.FLASK_DEBUG,
            'log_level': cls.LOG_LEVEL,
            'faq_file_path': cls.FAQ_FILE_PATH,
            'log_dir': cls.LOG_DIR,
            'openai_model': cls.OPENAI_MODEL,
            'max_faq_results': cls.MAX_FAQ_RESULTS,
            'max_message_length': cls.MAX_MESSAGE_LENGTH,
            'session_timeout': cls.SESSION_TIMEOUT
        }