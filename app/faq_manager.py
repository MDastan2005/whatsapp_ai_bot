"""
FAQ Manager
Модуль для управления базой частых вопросов
"""

import json
import logging
from typing import List, Dict, Optional
from config import Config

logger = logging.getLogger(__name__)

class FAQManager:
    """Менеджер для работы с базой FAQ"""
    
    def __init__(self):
        self.faq_file_path = Config.FAQ_FILE_PATH
        self.faq_data = []
        self.load_faq()
    
    def load_faq(self) -> bool:
        """
        Загружает FAQ из JSON файла
        
        Returns:
            bool: True если загрузка успешна
        """
        try:
            with open(self.faq_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.faq_data = data.get('faq', [])
            
            logger.info(f"Загружено {len(self.faq_data)} FAQ записей")
            return True
            
        except FileNotFoundError:
            logger.error(f"FAQ файл не найден: {self.faq_file_path}")
            self._create_default_faq()
            return False
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON файла FAQ: {e}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при загрузке FAQ: {e}")
            return False
    
    def _create_default_faq(self):
        """Создает файл FAQ по умолчанию"""
        default_faq = {
            "faq": [
                {
                    "id": 1,
                    "question": "Как оформить заказ?",
                    "answer": "Для оформления заказа свяжитесь с нашим менеджером или оставьте заявку на сайте. Мы перезвоним в течение 30 минут! 📞",
                    "keywords": ["заказ", "оформить", "купить", "заказать"]
                },
                {
                    "id": 2,
                    "question": "Какие способы оплаты доступны?",
                    "answer": "Мы принимаем наличные, банковские карты, переводы и онлайн-платежи. Выберите удобный способ! 💳",
                    "keywords": ["оплата", "способы", "платить", "деньги", "карта"]
                },
                {
                    "id": 3,
                    "question": "Сколько времени занимает доставка?",
                    "answer": "Доставка по городу занимает 1-2 дня, по области 2-3 дня. Точные сроки уточняйте у менеджера! 🚚",
                    "keywords": ["доставка", "сроки", "время", "когда", "быстро"]
                },
                {
                    "id": 4,
                    "question": "Есть ли гарантия на товар?",
                    "answer": "Да! На все товары предоставляется официальная гарантия производителя. Подробности уточняйте при заказе ✅",
                    "keywords": ["гарантия", "warranty", "качество", "замена"]
                },
                {
                    "id": 5,
                    "question": "Как связаться с поддержкой?",
                    "answer": "Вы можете написать нам здесь в WhatsApp, позвонить или отправить email. Мы всегда на связи! 📞📧",
                    "keywords": ["поддержка", "связаться", "контакты", "телефон", "помощь"]
                }
            ]
        }
        
        try:
            import os
            os.makedirs(os.path.dirname(self.faq_file_path), exist_ok=True)
            
            with open(self.faq_file_path, 'w', encoding='utf-8') as file:
                json.dump(default_faq, file, ensure_ascii=False, indent=2)
            
            self.faq_data = default_faq['faq']
            logger.info(f"Создан файл FAQ по умолчанию: {self.faq_file_path}")
            
        except Exception as e:
            logger.error(f"Ошибка создания файла FAQ по умолчанию: {e}")
    
    def search_faq(self, query: str, max_results: int = 3) -> List[Dict]:
        """
        Ищет релевантные FAQ записи по запросу
        
        Args:
            query: Поисковый запрос
            max_results: Максимальное количество результатов
            
        Returns:
            List[Dict]: Список релевантных FAQ записей
        """
        if not query or not self.faq_data:
            return []
        
        query_lower = query.lower()
        scored_results = []
        
        for faq_item in self.faq_data:
            score = self._calculate_relevance_score(query_lower, faq_item)
            if score > 0:
                scored_results.append((score, faq_item))
        
        # Сортируем по релевантности и берем топ результатов
        scored_results.sort(key=lambda x: x[0], reverse=True)
        
        results = [item[1] for item in scored_results[:max_results]]
        
        logger.debug(f"Найдено {len(results)} релевантных FAQ для запроса: '{query}'")
        return results
    
    def _calculate_relevance_score(self, query: str, faq_item: Dict) -> float:
        """
        Рассчитывает релевантность FAQ записи к запросу
        
        Args:
            query: Поисковый запрос (в нижнем регистре)
            faq_item: FAQ запись
            
        Returns:
            float: Оценка релевантности (чем выше, тем релевантнее)
        """
        score = 0.0
        
        # Проверяем совпадения в ключевых словах
        keywords = faq_item.get('keywords', [])
        for keyword in keywords:
            if keyword.lower() in query:
                score += 3.0  # Высокий вес для точных совпадений ключевых слов
        
        # Проверяем совпадения в вопросе
        question = faq_item.get('question', '').lower()
        query_words = query.split()
        
        for word in query_words:
            if len(word) > 2:  # Игнорируем короткие слова
                if word in question:
                    score += 2.0
                # Частичные совпадения
                elif any(word in q_word for q_word in question.split()):
                    score += 1.0
        
        # Проверяем совпадения в ответе (меньший вес)
        answer = faq_item.get('answer', '').lower()
        for word in query_words:
            if len(word) > 2 and word in answer:
                score += 0.5
        
        return score
    
    def get_all_faq(self) -> List[Dict]:
        """
        Возвращает все FAQ записи
        
        Returns:
            List[Dict]: Все FAQ записи
        """
        return self.faq_data.copy()
    
    def get_faq_by_id(self, faq_id: int) -> Optional[Dict]:
        """
        Возвращает FAQ запись по ID
        
        Args:
            faq_id: ID записи
            
        Returns:
            Dict или None: FAQ запись или None если не найдена
        """
        for item in self.faq_data:
            if item.get('id') == faq_id:
                return item.copy()
        return None
    
    def add_faq_item(self, question: str, answer: str, keywords: Optional[List[str]] = None) -> bool:
        """
        Добавляет новую FAQ запись
        
        Args:
            question: Вопрос
            answer: Ответ
            keywords: Ключевые слова
            
        Returns:
            bool: True если добавление успешно
        """
        try:
            # Валидация входных данных
            if not question or not isinstance(question, str) or len(question.strip()) == 0:
                logger.error("Вопрос не может быть пустым")
                return False
                
            if not answer or not isinstance(answer, str) or len(answer.strip()) == 0:
                logger.error("Ответ не может быть пустым")
                return False
            
            # Очищаем и валидируем ключевые слова
            if keywords is None:
                keywords = []
            elif not isinstance(keywords, list):
                logger.error("Ключевые слова должны быть списком")
                return False
            else:
                # Фильтруем валидные ключевые слова
                keywords = [kw.strip() for kw in keywords if kw and isinstance(kw, str) and len(kw.strip()) > 0]
            
            # Определяем новый ID
            max_id = max([item.get('id', 0) for item in self.faq_data], default=0)
            new_id = max_id + 1
            
            new_item = {
                'id': new_id,
                'question': question.strip(),
                'answer': answer.strip(),
                'keywords': keywords
            }
            
            self.faq_data.append(new_item)
            
            # Сохраняем в файл
            return self.save_faq()
            
        except Exception as e:
            logger.error(f"Ошибка добавления FAQ записи: {e}")
            return False
    
    def update_faq_item(self, faq_id: int, question: Optional[str] = None, answer: Optional[str] = None, keywords: Optional[List[str]] = None) -> bool:
        """
        Обновляет существующую FAQ запись
        
        Args:
            faq_id: ID записи для обновления
            question: Новый вопрос (опционально)
            answer: Новый ответ (опционально)
            keywords: Новые ключевые слова (опционально)
            
        Returns:
            bool: True если обновление успешно
        """
        try:
            for item in self.faq_data:
                if item.get('id') == faq_id:
                    if question is not None:
                        item['question'] = question
                    if answer is not None:
                        item['answer'] = answer
                    if keywords is not None:
                        item['keywords'] = keywords
                    
                    return self.save_faq()
            
            logger.warning(f"FAQ запись с ID {faq_id} не найдена")
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обновления FAQ записи: {e}")
            return False
    
    def delete_faq_item(self, faq_id: int) -> bool:
        """
        Удаляет FAQ запись по ID
        
        Args:
            faq_id: ID записи для удаления
            
        Returns:
            bool: True если удаление успешно
        """
        try:
            original_length = len(self.faq_data)
            self.faq_data = [item for item in self.faq_data if item.get('id') != faq_id]
            
            if len(self.faq_data) < original_length:
                return self.save_faq()
            else:
                logger.warning(f"FAQ запись с ID {faq_id} не найдена")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка удаления FAQ записи: {e}")
            return False
    
    def save_faq(self) -> bool:
        """
        Сохраняет FAQ в файл
        
        Returns:
            bool: True если сохранение успешно
        """
        try:
            faq_structure = {'faq': self.faq_data}
            
            with open(self.faq_file_path, 'w', encoding='utf-8') as file:
                json.dump(faq_structure, file, ensure_ascii=False, indent=2)
            
            logger.info(f"FAQ успешно сохранен в {self.faq_file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения FAQ: {e}")
            return False
    
    def reload_faq(self) -> bool:
        """
        Перезагружает FAQ из файла
        
        Returns:
            bool: True если перезагрузка успешна
        """
        logger.info("Перезагрузка FAQ...")
        return self.load_faq()
    
    def get_faq_stats(self) -> Dict:
        """
        Возвращает статистику FAQ
        
        Returns:
            Dict: Статистика FAQ
        """
        return {
            'total_items': len(self.faq_data),
            'total_keywords': sum(len(item.get('keywords', [])) for item in self.faq_data),
            'average_keywords_per_item': round(
                sum(len(item.get('keywords', [])) for item in self.faq_data) / len(self.faq_data), 2
            ) if self.faq_data else 0,
            'file_path': self.faq_file_path
        }