"""
OpenAI API Client
Модуль для работы с OpenAI GPT API
"""

import logging
from typing import Optional, List, Dict
import openai
from config import Config

logger = logging.getLogger(__name__)

class OpenAIClient:
    """Клиент для работы с OpenAI API"""
    
    def __init__(self):
        self.model = "gpt-3.5-turbo"
        self.api_key = None
    
    def generate_faq_response(self, user_question: str, faq_context: List[Dict]) -> Optional[str]:
        """
        Генерирует ответ на основе FAQ контекста
        
        Args:
            user_question: Вопрос пользователя
            faq_context: Список FAQ элементов
            
        Returns:
            str: Сгенерированный ответ или None при ошибке
        """
        try:
            system_prompt = self._get_system_prompt()
            user_prompt = self._format_user_prompt(user_question, self._format_faq_context(faq_context))
            
            # Новый API openai>=1.0.0
            try:
                response = openai.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                content = response.choices[0].message.content
                answer = content.strip() if content else ""
            except AttributeError:
                # Старый API fallback
                ChatCompletion = getattr(openai, 'ChatCompletion', None)
                Completion = getattr(openai, 'Completion', None)
                if ChatCompletion:
                    response = ChatCompletion.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        max_tokens=500,
                        temperature=0.7
                    )
                    content = response.choices[0].message['content']
                    answer = content.strip() if content else ""
                elif Completion:
                    prompt = f"{system_prompt}\n{user_prompt}"
                    response = Completion.create(
                        engine=self.model,
                        prompt=prompt,
                        max_tokens=500,
                        temperature=0.7
                    )
                    answer = response.choices[0].text.strip()
                else:
                    logger.error("OpenAI SDK не поддерживает нужные методы.")
                    return None
            
            logger.info(f"OpenAI сгенерировал ответ длиной {len(answer)} символов")
            
            return answer
            
        except Exception as e:
            logger.error(f"Ошибка при генерации ответа OpenAI: {e}")
            return None
    
    def _get_system_prompt(self) -> str:
        """Возвращает системный промпт для GPT"""
        return """
Ты — помощник службы поддержки клиентов компании. Твои правила:

1. Отвечай ТОЛЬКО на основе информации из FAQ, которую тебе предоставили ниже.
2. НЕ придумывай и НЕ выдумывай никакой информации, которой нет в FAQ.
3. Если в FAQ нет точного ответа — честно скажи об этом и предложи обратиться к менеджеру или поддержке.
4. НЕ делай предположений о политике компании, ценах, условиях и т.д. — только то, что есть в FAQ.
5. Отвечай на русском языке дружелюбно и профессионально.
6. Будь кратким, но информативным (максимум 3-4 предложения).
7. Используй эмодзи для дружелюбности, но умеренно.

Если нет информации — обязательно напиши: «К сожалению, у меня нет точного ответа на этот вопрос. Пожалуйста, обратитесь к нашему менеджеру — он обязательно поможет!»
"""
    
    def _format_user_prompt(self, user_question: str, context: str) -> str:
        """Форматирует промпт пользователя"""
        return f"""База знаний FAQ:
{context}

Вопрос клиента: \"{user_question}\"

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
            # Новый API openai>=1.0.0
            try:
                response = openai.chat.completions.create(
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
                content = response.choices[0].message.content
                intent = content.strip().lower() if content else "other"
            except AttributeError:
                ChatCompletion = getattr(openai, 'ChatCompletion', None)
                Completion = getattr(openai, 'Completion', None)
                if ChatCompletion:
                    response = ChatCompletion.create(
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
                    content = response.choices[0].message['content']
                    intent = content.strip().lower() if content else "other"
                elif Completion:
                    prompt = f"Классифицируй намерение пользователя: {user_message}\nОтветь одним словом."
                    response = Completion.create(
                        engine=self.model,
                        prompt=prompt,
                        max_tokens=10,
                        temperature=0.1
                    )
                    intent = response.choices[0].text.strip().lower()
                else:
                    logger.error("OpenAI SDK не поддерживает нужные методы.")
                    return "other"
            logger.debug(f"Классифицировано намерение: {intent}")
            
            return intent
            
        except Exception as e:
            logger.error(f"Ошибка классификации намерения: {e}")
            return "other"
    
    def generate_greeting_response(self, user_name: Optional[str] = None) -> str:
        """
        Генерирует приветственное сообщение
        
        Args:
            user_name: Имя пользователя (опционально)
            
        Returns:
            str: Приветственное сообщение
        """
        try:
            name_part = f" {user_name}" if user_name else ""
            
            # Новый API openai>=1.0.0
            try:
                response = openai.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": """Создай дружелюбное приветственное сообщение для клиента в WhatsApp чате службы поддержки. \nСообщение должно быть:\n- На русском языке\n- Коротким (1-2 предложения)\n- Дружелюбным с 1-2 эмодзи\n- Предлагать помощь"""
                        },
                        {
                            "role": "user",
                            "content": f"Поприветствуй клиента{name_part}"
                        }
                    ],
                    max_tokens=100,
                    temperature=0.8
                )
                content = response.choices[0].message.content
                greeting = content.strip() if content else f"Привет{name_part}! 👋 Как могу помочь?"
            except AttributeError:
                ChatCompletion = getattr(openai, 'ChatCompletion', None)
                Completion = getattr(openai, 'Completion', None)
                if ChatCompletion:
                    response = ChatCompletion.create(
                        model=self.model,
                        messages=[
                            {
                                "role": "system",
                                "content": """Создай дружелюбное приветственное сообщение для клиента в WhatsApp чате службы поддержки. \nСообщение должно быть:\n- На русском языке\n- Коротким (1-2 предложения)\n- Дружелюбным с 1-2 эмодзи\n- Предлагать помощь"""
                            },
                            {
                                "role": "user",
                                "content": f"Поприветствуй клиента{name_part}"
                            }
                        ],
                        max_tokens=100,
                        temperature=0.8
                    )
                    content = response.choices[0].message['content']
                    greeting = content.strip() if content else f"Привет{name_part}! 👋 Как могу помочь?"
                elif Completion:
                    prompt = f"Поприветствуй клиента{name_part} в WhatsApp, коротко, дружелюбно, с эмодзи."
                    response = Completion.create(
                        engine=self.model,
                        prompt=prompt,
                        max_tokens=100,
                        temperature=0.8
                    )
                    greeting = response.choices[0].text.strip()
                else:
                    logger.error("OpenAI SDK не поддерживает нужные методы.")
                    return f"Привет{name_part}! 👋 Как могу помочь?"
            
            logger.debug(f"Сгенерировано приветствие: {greeting}")
            return greeting
            
        except Exception as e:
            logger.error(f"Ошибка генерации приветствия: {e}")
            name_part = f" {user_name}" if user_name else ""
            return f"Привет{name_part}! �� Как могу помочь?"