#!/usr/bin/env python3
"""
WhatsApp FAQ Bot - Главный файл запуска
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask, request, jsonify, make_response

# Добавляем текущую директорию в путь Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from app.bot import WhatsAppBot

# Глобальные переменные
bot = None
logger = logging.getLogger(__name__)

def setup_logging():
    """Настраивает систему логирования"""
    if not os.path.exists(Config.LOG_DIR):
        os.makedirs(Config.LOG_DIR)
    
    log_filename = f"{Config.LOG_DIR}/bot_{datetime.now().strftime('%Y-%m-%d')}.log"
    
    # Настройка форматирования
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Обработчик для файла
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # Обработчик для консоли
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Настройка root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    logger.info(f"Логирование настроено, уровень: {Config.LOG_LEVEL}")

def create_app():
    """Создает Flask приложение"""
    app = Flask(__name__)
    
    # Установка максимального размера тела запроса
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
    
    @app.route('/', methods=['GET'])
    def health_check():
        """Проверка состояния сервиса"""
        try:
            stats = bot.get_bot_stats() if bot else {'status': 'initializing'}
            return jsonify({
                'status': 'running',
                'service': 'WhatsApp FAQ Bot',
                'timestamp': datetime.now().isoformat(),
                'bot_stats': stats,
                'config': Config.get_config_dict()
            })
        except Exception as e:
            logger.error(f"Ошибка в health check: {e}")
            return jsonify({'error': 'Service unavailable'}), 503
    
    @app.route('/stats', methods=['GET'])
    def get_stats():
        """Получение статистики бота"""
        try:
            if not bot:
                return jsonify({'error': 'Bot not initialized'}), 503
            
            stats = bot.get_bot_stats()
            return jsonify(stats)
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return jsonify({'error': 'Failed to get stats'}), 500
    
    @app.route('/reload-faq', methods=['POST'])
    def reload_faq():
        """Перезагрузка базы FAQ"""
        try:
            if not bot:
                return jsonify({'error': 'Bot not initialized'}), 503
            
            success = bot.reload_faq()
            if success:
                return jsonify({'status': 'success', 'message': 'FAQ reloaded'})
            else:
                return jsonify({'error': 'Failed to reload FAQ'}), 500
        except Exception as e:
            logger.error(f"Ошибка перезагрузки FAQ: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/webhook', methods=['GET'])
    def verify_webhook():
        """Верификация webhook для WhatsApp"""
        try:
            mode = request.args.get('hub.mode')
            token = request.args.get('hub.verify_token')
            challenge = request.args.get('hub.challenge')
            
            logger.info(f"Webhook verification attempt: mode={mode}, token_match={token == Config.WEBHOOK_VERIFY_TOKEN}")
            
            if mode == 'subscribe' and token == Config.WEBHOOK_VERIFY_TOKEN:
                logger.info("Webhook верифицирован успешно")
                return make_response(challenge, 200)
            else:
                logger.warning("Неверный токен верификации webhook")
                return make_response('Forbidden', 403)
                
        except Exception as e:
            logger.error(f"Ошибка верификации webhook: {e}")
            return make_response('Internal Server Error', 500)
    
    @app.route('/webhook', methods=['POST'])
    def handle_webhook():
        """Обработка входящих сообщений от WhatsApp"""
        try:
            # Проверяем, что бот инициализирован
            if not bot:
                logger.error("Бот не инициализирован")
                return jsonify({'error': 'Bot not initialized'}), 503
            
            # Получаем данные
            data = request.get_json()
            
            if not data:
                logger.warning("Получен пустой запрос webhook")
                return jsonify({'status': 'no_data'}), 400
            
            logger.debug(f"Получены данные webhook: {data}")
            
            # Обработка сообщения ботом
            success = bot.handle_message(data)
            
            if success:
                return jsonify({'status': 'success'})
            else:
                return jsonify({'status': 'no_action_needed'})
                
        except Exception as e:
            logger.error(f"Ошибка обработки webhook: {e}")
            return jsonify({'error': 'Internal Server Error'}), 500
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

def initialize_bot():
    """Инициализирует бота"""
    global bot
    try:
        logger.info("Инициализация WhatsApp бота...")
        bot = WhatsAppBot()
        logger.info("Бот успешно инициализирован")
        return True
    except Exception as e:
        logger.error(f"Ошибка инициализации бота: {e}")
        return False

def main():
    """Главная функция запуска приложения"""
    try:
        print("=" * 50)
        print("🤖 WhatsApp FAQ Bot")
        print("=" * 50)
        
        # Настройка логирования
        setup_logging()
        
        # Проверка конфигурации
        logger.info("Проверка конфигурации...")
        Config.validate_config()
        logger.info("✅ Конфигурация валидна")
        
        # Создание необходимых директорий
        os.makedirs('data', exist_ok=True)
        os.makedirs(Config.LOG_DIR, exist_ok=True)
        
        # Инициализация бота
        if not initialize_bot():
            raise Exception("Не удалось инициализировать бота")
        
        # Создание приложения
        app = create_app()
        
        logger.info(f"🚀 Запуск сервера на порту {Config.FLASK_PORT}")
        logger.info(f"🔧 Debug режим: {'включен' if Config.FLASK_DEBUG else 'выключен'}")
        
        # Запуск сервера
        app.run(
            host='0.0.0.0',
            port=Config.FLASK_PORT,
            debug=Config.FLASK_DEBUG,
            use_reloader=False  # Отключаем reloader для избежания двойной инициализации
        )
        
    except ValueError as e:
        print(f"❌ Ошибка конфигурации: {e}")
        print("💡 Пожалуйста, проверьте файл .env")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
        if logger:
            logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()