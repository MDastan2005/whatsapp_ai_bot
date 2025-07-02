"""
OpenAI API Client
Модуль для работы с OpenAI GPT API
"""

import logging
from typing import Optional, List, Dict
from openai import OpenAI
from config import Config

logger = logging.getLogger(__name__)

class OpenAIClient:
    """Клиент для работы с OpenAI API"""
    
    def __init__(self):
        if not Config.OPENAI_API_KEY:
            raise ValueError("OpenAI API ключ не настроен")
        
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = "gpt-3.5-turbo"  # Можно изменить на gpt-4 при необходимости
    
    def generate_faq_response(self, user_question: str, faq_context: List[Dict]) -> Optional[str]:
        """
        Генерирует ответ на основе вопроса пользователя и FAQ базы
        
        Args:
            user_question: Вопрос пользователя
            faq_context: Список релевантных FAQ записей
            
        Returns:
            str: Сгенерированный ответ или None при ошибке
        """
        try:
            # Формируем контекст из FAQ
            context_text = self._format_faq_context(faq_context)
            
            # Создаем промпт
            system_prompt = self._get_system_prompt()
            user_prompt = self._format_user_prompt(user_question, context_text)
            
            # Отправляем запрос к OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content.strip()
            logger.info(f"OpenAI сгенерировал ответ длиной {len(answer)} символов")
            
            return answer
            
        except Exception as e:
            logger.error(f"Ошибка при генерации ответа OpenAI: {e}")
            return None
    
    def _get_system_prompt(self) -> str:
        """Возвращает системный промпт для GPT"""
        return """Ты - помощник службы поддержки клиентов. Твоя задача:

1. Отвечать на русском языке дружелюбно и профессионально
2. Использовать предоставленную информацию из базы FAQ для ответов
3. Если точного ответа нет в FAQ, сказать об этом и предложить связаться с поддержкой
4. Быть кратким, но информативным
5. Использовать эмодзи для дружелюбности, но умеренно

Правила:
- Не выдумывай информацию, которой нет в FAQ
- Если вопрос не связан с FAQ, вежливо перенаправь к поддержке
- Отвечай максимум в 3-4 предложениях"""
    
    def _format_user_prompt(self, user_question: str, context: str) -> str:
        """Форматирует промпт пользователя"""
        return f"""База знаний FAQ:
{context}

Вопрос клиента: "{user_question}"

Ответь на вопрос клиента, используя информацию из базы FAQ выше."""
    
    def _format_faq_context(self, faq_items: List[Dict]) -> str:
        """Форматирует FAQ элементы в текстовый контекст"""
        if not faq_items:
            return "FAQ база пуста."
        
        context_parts = []
        for item in faq_items:
            context_parts.append(f"Q: {item.get('question', '')}\nA: {item.get('answer', '')}")
        
        return "\n\n".join(context_parts)
    
    def classify_intent(self, user_message: str) -> str:
        """
        Классифицирует намерение пользователя
        
        Args:
            user_message: Сообщение пользователя
            
        Returns:
            str: Классификация намерения
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """Классифицируй намерение пользователя по одной из категорий:
- question: Вопрос о продукте/услуге
- complaint: Жалоба или проблема
- order: Заказ или покупка
- support: Техническая поддержка
- greeting: Приветствие
- other: Другое

Ответь только одним словом - названием категории."""
                    },
                    {"role": "user", "content": user_message}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            intent = response.choices[0].message.content.strip().lower()
            logger.debug(f"Классифицировано намерение: {intent}")
            
            return intent
            
        except Exception as e:
            logger.error(f"Ошибка классификации намерения: {e}")
            return "other"
    
    def generate_greeting_response(self, user_name: str = None) -> str:
        """
        Генерирует приветственное сообщение
        
        Args:
            user_name: Имя пользователя (опционально)
            
        Returns:
            str: Приветственное сообщение
        """
        try:
            name_part = f" {user_name}" if user_name else ""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """Создай дружелюбное приветственное сообщение для клиента в WhatsApp чате службы поддержки. 
Сообщение должно быть:
- На русском языке
- Коротким (1-2 предложения)
- Дружелюбным с 1-2 эмодзи
- Предлагать помощь"""
                    },
                    {
                        "role": "user",
                        "content": f"Поприветствуй клиента{name_part}"
                    }
                ],
                max_tokens=100,
                temperature=0.8
            )
            
            greeting = response.choices[0].message.content.strip()
            return greeting
            
        except Exception as e:
            logger.error(f"Ошибка генерации приветствия: {e}")
            return f"Привет{name_part}! 👋 Как могу помочь?"