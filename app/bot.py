"""
WhatsApp Bot Main Logic
Основная логика WhatsApp бота для обработки FAQ
"""

import logging
from typing import Dict, Optional, List
from .whatsapp_client import WhatsAppClient
from .openai_client import OpenAIClient
from .faq_manager import FAQManager

logger = logging.getLogger(__name__)

class WhatsAppBot:
    """Основной класс WhatsApp бота"""
    
    def __init__(self):
        """Инициализация бота"""
        try:
            self.whatsapp = WhatsAppClient()
            self.openai = OpenAIClient()
            self.faq = FAQManager()
            
            # Кэш для хранения состояния пользователей
            self.user_sessions = {}
            
            logger.info("WhatsApp бот успешно инициализирован")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации бота: {e}")
            raise
    
    def handle_message(self, webhook_data: Dict) -> bool:
        """
        Обрабатывает входящее сообщение от WhatsApp
        
        Args:
            webhook_data: Данные от WhatsApp webhook
            
        Returns:
            bool: True если сообщение обработано
        """
        try:
            # Извлекаем данные сообщения
            message_data = self.whatsapp.extract_message_data(webhook_data)
            
            if not message_data:
                logger.debug("Нет данных сообщения для обработки")
                return False
            
            # Проверяем тип сообщения
            if message_data['type'] != 'text' or not message_data['text']:
                logger.debug(f"Пропускаем сообщение типа: {message_data['type']}")
                return False
            
            user_phone = message_data['from']
            user_message = message_data['text'].strip()
            message_id = message_data['message_id']
            user_name = message_data.get('contact_name')
            
            logger.info(f"Обработка сообщения от {user_phone}: '{user_message}'")
            
            # Отмечаем сообщение как прочитанное
            self.whatsapp.mark_message_as_read(message_id)
            
            # Обрабатываем сообщение и получаем ответ
            response = self._process_user_message(user_phone, user_message, user_name)
            
            if response:
                # Отправляем ответ пользователю
                success = self.whatsapp.send_text_message(user_phone, response)
                
                if success:
                    logger.info(f"Ответ отправлен пользователю {user_phone}")
                    return True
                else:
                    logger.error(f"Не удалось отправить ответ пользователю {user_phone}")
                    return False
            else:
                logger.warning("Не удалось сгенерировать ответ")
                return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки сообщения: {e}")
            return False
    
    def _process_user_message(self, user_phone: str, message: str, user_name: str = None) -> Optional[str]:
        """
        Обрабатывает сообщение пользователя и генерирует ответ
        
        Args:
            user_phone: Номер телефона пользователя
            message: Текст сообщения
            user_name: Имя пользователя (опционально)
            
        Returns:
            str: Ответ для пользователя или None
        """
        try:
            # Получаем или создаем сессию пользователя
            user_session = self._get_user_session(user_phone)
            
            # Классифицируем намерение пользователя
            intent = self.openai.classify_intent(message)
            logger.debug(f"Определено намерение: {intent}")
            
            # Обрабатываем разные типы намерений
            if intent == 'greeting' and not user_session.get('greeted'):
                # Первое приветствие
                response = self.openai.generate_greeting_response(user_name)
                user_session['greeted'] = True
                return response
            
            elif intent in ['question', 'support', 'order', 'complaint']:
                # Ищем релевантные FAQ
                relevant_faq = self.faq.search_faq(message, max_results=3)
                
                if relevant_faq:
                    # Генерируем ответ на основе FAQ
                    response = self.openai.generate_faq_response(message, relevant_faq)
                    
                    if response:
                        # Сохраняем статистику
                        self._update_user_stats(user_phone, message, len(relevant_faq))
                        return response
                
                # Если нет подходящих FAQ или не удалось сгенерировать ответ
                return self._get_fallback_response()
            
            else:
                # Для других типов сообщений пытаемся найти FAQ
                relevant_faq = self.faq.search_faq(message, max_results=2)
                
                if relevant_faq:
                    response = self.openai.generate_faq_response(message, relevant_faq)
                    if response:
                        return response
                
                return self._get_general_help_response()
            
        except Exception as e:
            logger.error(f"Ошибка обработки сообщения пользователя: {e}")
            return self._get_error_response()
    
    def _get_user_session(self, user_phone: str) -> Dict:
        """
        Получает или создает сессию пользователя
        
        Args:
            user_phone: Номер телефона пользователя
            
        Returns:
            Dict: Сессия пользователя
        """
        if user_phone not in self.user_sessions:
            self.user_sessions[user_phone] = {
                'greeted': False,
                'message_count': 0,
                'last_message_time': None,
                'topics': []
            }
        
        return self.user_sessions[user_phone]
    
    def _update_user_stats(self, user_phone: str, message: str, faq_matches: int):
        """
        Обновляет статистику пользователя
        
        Args:
            user_phone: Номер телефона
            message: Сообщение
            faq_matches: Количество найденных FAQ
        """
        try:
            session = self._get_user_session(user_phone)
            session['message_count'] += 1
            session['last_message_time'] = None  # Можно добавить timestamp
            
            # Классифицируем тему сообщения для аналитики
            if faq_matches > 0:
                # Можно добавить логику определения темы
                pass
            
        except Exception as e:
            logger.error(f"Ошибка обновления статистики пользователя: {e}")
    
    def _get_fallback_response(self) -> str:
        """Возвращает резервный ответ когда нет подходящих FAQ"""
        return """К сожалению, я не нашел точной информации по вашему вопросу в нашей базе знаний 😔

Пожалуйста, обратитесь к нашему менеджеру для получения подробной консультации. Мы обязательно поможем! 

📞 Менеджер ответит в рабочее время
💬 Или опишите вопрос подробнее"""
    
    def _get_general_help_response(self) -> str:
        """Возвращает общий ответ помощи"""
        return """Привет! 👋 Я бот-помощник нашей компании.

Я могу помочь с:
• Информацией о товарах и услугах
• Условиями заказа и доставки  
• Способами оплаты
• Гарантийными вопросами

Просто задайте ваш вопрос, и я постараюсь помочь! 😊"""
    
    def _get_error_response(self) -> str:
        """Возвращает ответ при технической ошибке"""
        return """Извините, произошла техническая ошибка ⚠️

Пожалуйста, попробуйте повторить запрос через несколько минут или обратитесь к нашему менеджеру.

Приносим извинения за неудобства! 🙏"""
    
    def get_bot_stats(self) -> Dict:
        """
        Возвращает статистику работы бота
        
        Returns:
            Dict: Статистика бота
        """
        try:
            total_users = len(self.user_sessions)
            total_messages = sum(session.get('message_count', 0) for session in self.user_sessions.values())
            
            faq_stats = self.faq.get_faq_stats()
            
            return {
                'total_users': total_users,
                'total_messages': total_messages,
                'average_messages_per_user': round(total_messages / total_users, 2) if total_users > 0 else 0,
                'faq_items': faq_stats['total_items'],
                'status': 'active'
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики бота: {e}")
            return {'error': 'Не удалось получить статистику'}
    
    def reload_faq(self) -> bool:
        """
        Перезагружает базу FAQ
        
        Returns:
            bool: True если перезагрузка успешна
        """
        try:
            success = self.faq.reload_faq()
            if success:
                logger.info("База FAQ успешно перезагружена")
            return success
        except Exception as e:
            logger.error(f"Ошибка перезагрузки FAQ: {e}")
            return False