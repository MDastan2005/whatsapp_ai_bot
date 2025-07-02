"""
WhatsApp Business API Client
Модуль для работы с WhatsApp Business API
"""

import requests
import logging
from typing import Dict, Optional
from config import Config

logger = logging.getLogger(__name__)

class WhatsAppClient:
    """Клиент для работы с WhatsApp Business API"""
    
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v18.0"
        self.token = Config.WHATSAPP_TOKEN
        self.phone_number_id = Config.WHATSAPP_PHONE_NUMBER_ID
        
        if not self.token or not self.phone_number_id:
            raise ValueError("WhatsApp токен или ID номера телефона не настроены")
    
    def send_text_message(self, recipient_phone: str, message: str) -> bool:
        """
        Отправляет текстовое сообщение
        
        Args:
            recipient_phone: Номер получателя
            message: Текст сообщения
            
        Returns:
            bool: True если сообщение отправлено успешно
        """
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "to": recipient_phone,
                "type": "text",
                "text": {
                    "body": message
                }
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                logger.info(f"Сообщение отправлено успешно на {recipient_phone}")
                return True
            else:
                logger.error(f"Ошибка отправки сообщения: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Исключение при отправке сообщения: {e}")
            return False
    
    def send_template_message(self, recipient_phone: str, template_name: str, language_code: str = "ru") -> bool:
        """
        Отправляет шаблонное сообщение
        
        Args:
            recipient_phone: Номер получателя
            template_name: Название шаблона
            language_code: Код языка
            
        Returns:
            bool: True если сообщение отправлено успешно
        """
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "to": recipient_phone,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": language_code
                    }
                }
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                logger.info(f"Шаблон {template_name} отправлен успешно на {recipient_phone}")
                return True
            else:
                logger.error(f"Ошибка отправки шаблона: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Исключение при отправке шаблона: {e}")
            return False
    
    def mark_message_as_read(self, message_id: str) -> bool:
        """
        Отмечает сообщение как прочитанное
        
        Args:
            message_id: ID сообщения
            
        Returns:
            bool: True если операция успешна
        """
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                logger.debug(f"Сообщение {message_id} отмечено как прочитанное")
                return True
            else:
                logger.warning(f"Не удалось отметить сообщение как прочитанное: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Исключение при отметке сообщения как прочитанное: {e}")
            return False
    
    def extract_message_data(self, webhook_data: Dict) -> Optional[Dict]:
        """
        Извлекает данные сообщения из webhook
        
        Args:
            webhook_data: Данные от WhatsApp webhook
            
        Returns:
            Dict с данными сообщения или None
        """
        try:
            if not webhook_data.get('entry'):
                return None
            
            entry = webhook_data['entry'][0]
            changes = entry.get('changes', [])
            
            if not changes:
                return None
            
            change = changes[0]
            value = change.get('value', {})
            messages = value.get('messages', [])
            
            if not messages:
                return None
            
            message = messages[0]
            
            # Извлекаем основную информацию
            message_data = {
                'message_id': message.get('id'),
                'from': message.get('from'),
                'timestamp': message.get('timestamp'),
                'type': message.get('type'),
                'text': None
            }
            
            # Извлекаем текст сообщения
            if message_data['type'] == 'text':
                message_data['text'] = message.get('text', {}).get('body')
            
            # Извлекаем контакты из webhook
            contacts = value.get('contacts', [])
            if contacts:
                contact = contacts[0]
                message_data['contact_name'] = contact.get('profile', {}).get('name')
            
            logger.debug(f"Извлечены данные сообщения: {message_data}")
            return message_data
            
        except Exception as e:
            logger.error(f"Ошибка извлечения данных сообщения: {e}")
            return None