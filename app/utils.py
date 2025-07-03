"""
Utility functions for WhatsApp FAQ Bot
Утилиты для WhatsApp FAQ бота
"""

import re
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def sanitize_phone_number(phone: str) -> str:
    """
    Очищает и форматирует номер телефона
    
    Args:
        phone: Номер телефона в любом формате
        
    Returns:
        str: Очищенный номер телефона
    """
    if not phone:
        return ""
    
    # Удаляем все символы кроме цифр
    cleaned = re.sub(r'[^\d]', '', str(phone))
    
    # Убираем код страны если он 7 или 8 и добавляем 7
    if len(cleaned) == 11 and cleaned.startswith(('7', '8')):
        cleaned = '7' + cleaned[1:]
    
    # Если номер начинается с 9 и имеет 10 цифр, добавляем 7
    if len(cleaned) == 10 and cleaned.startswith('9'):
        cleaned = '7' + cleaned
    
    return cleaned


def validate_phone_number(phone: str) -> bool:
    """
    Проверяет валидность номера телефона
    
    Args:
        phone: Номер телефона
        
    Returns:
        bool: True если номер валиден
    """
    if not phone:
        return False
    
    cleaned = sanitize_phone_number(phone)
    
    # Проверяем что номер имеет правильную длину и формат
    if len(cleaned) == 11 and cleaned.startswith('7'):
        return True
    
    return False


def extract_keywords_from_text(text: str, max_keywords: int = 5) -> List[str]:
    """
    Извлекает ключевые слова из текста
    
    Args:
        text: Исходный текст
        max_keywords: Максимальное количество ключевых слов
        
    Returns:
        List[str]: Список ключевых слов
    """
    if not text:
        return []
    
    # Удаляем знаки препинания и приводим к нижнему регистру
    cleaned_text = re.sub(r'[^\w\s]', ' ', text.lower())
    
    # Разбиваем на слова
    words = cleaned_text.split()
    
    # Фильтруем стоп-слова (можно расширить список)
    stop_words = {
        'и', 'в', 'во', 'не', 'что', 'он', 'на', 'я', 'с', 'со', 'как', 'а', 'то', 'все', 'она',
        'так', 'его', 'но', 'да', 'ты', 'к', 'у', 'же', 'вы', 'за', 'бы', 'по', 'только', 'ее',
        'мне', 'было', 'вот', 'от', 'меня', 'еще', 'нет', 'о', 'из', 'ему', 'теперь', 'когда',
        'даже', 'ну', 'вдруг', 'ли', 'если', 'уже', 'или', 'ни', 'быть', 'был', 'него', 'до',
        'вас', 'нибудь', 'опять', 'уж', 'вам', 'ведь', 'там', 'потом', 'себя', 'ничего', 'ей',
        'может', 'они', 'тут', 'где', 'есть', 'надо', 'ней', 'для', 'мы', 'тебя', 'их', 'чем',
        'была', 'сам', 'чтоб', 'без', 'будто', 'чего', 'раз', 'тоже', 'себе', 'под', 'будет',
        'ж', 'тогда', 'кто', 'этот', 'того', 'потому', 'этого', 'какой', 'совсем', 'ним', 'здесь',
        'этом', 'один', 'почти', 'мой', 'тем', 'чтобы', 'нее', 'сейчас', 'были', 'куда', 'зачем',
        'всех', 'никогда', 'можно', 'при', 'наконец', 'два', 'об', 'другой', 'хоть', 'после',
        'над', 'больше', 'тот', 'через', 'эти', 'нас', 'про', 'всего', 'них', 'какая', 'много',
        'разве', 'три', 'эту', 'моя', 'впрочем', 'хорошо', 'свою', 'этой', 'перед', 'иногда',
        'лучше', 'чуть', 'том', 'нельзя', 'такой', 'им', 'более', 'всегда', 'притом', 'будет',
        'очень', 'насчет', 'вдвоем', 'подобно', 'почему', 'долго', 'пока', 'лишь', 'быстро',
        'сказал', 'либо', 'против', 'конец', 'всякий', 'даже', 'все', 'всех', 'всего', 'всегда',
        'всегда', 'всегда', 'всегда', 'всегда', 'всегда', 'всегда', 'всегда', 'всегда', 'всегда'
    }
    
    # Фильтруем слова
    filtered_words = []
    for word in words:
        if (len(word) > 2 and 
            word not in stop_words and 
            not word.isdigit() and
            word not in filtered_words):
            filtered_words.append(word)
    
    # Возвращаем топ ключевых слов
    return filtered_words[:max_keywords]


def format_message_for_logging(message: str, max_length: int = 100) -> str:
    """
    Форматирует сообщение для логирования
    
    Args:
        message: Исходное сообщение
        max_length: Максимальная длина для логирования
        
    Returns:
        str: Отформатированное сообщение
    """
    if not message:
        return ""
    
    if len(message) <= max_length:
        return message
    
    return message[:max_length] + "..."


def calculate_response_time(start_time: datetime) -> float:
    """
    Вычисляет время ответа в секундах
    
    Args:
        start_time: Время начала обработки
        
    Returns:
        float: Время ответа в секундах
    """
    if not start_time:
        return 0.0
    
    end_time = datetime.now()
    return (end_time - start_time).total_seconds()


def is_message_too_old(timestamp: str, max_age_hours: int = 24) -> bool:
    """
    Проверяет, не слишком ли старое сообщение
    
    Args:
        timestamp: Unix timestamp сообщения
        max_age_hours: Максимальный возраст в часах
        
    Returns:
        bool: True если сообщение слишком старое
    """
    try:
        message_time = datetime.fromtimestamp(int(timestamp))
        current_time = datetime.now()
        age = current_time - message_time
        
        return age > timedelta(hours=max_age_hours)
    except (ValueError, TypeError, OSError) as e:
        logger.warning(f"Ошибка проверки времени сообщения: {e}")
        return False


def rate_limit_check(user_phone: str, user_sessions: Dict, max_messages_per_hour: int = 10) -> bool:
    """
    Проверяет лимит сообщений от пользователя
    
    Args:
        user_phone: Номер телефона пользователя
        user_sessions: Сессии пользователей
        max_messages_per_hour: Максимальное количество сообщений в час
        
    Returns:
        bool: True если лимит не превышен
    """
    if user_phone not in user_sessions:
        return True
    
    session = user_sessions[user_phone]
    current_time = datetime.now()
    
    # Инициализируем историю сообщений если её нет
    if 'message_history' not in session:
        session['message_history'] = []
    
    # Удаляем сообщения старше часа
    hour_ago = current_time - timedelta(hours=1)
    session['message_history'] = [
        msg_time for msg_time in session['message_history']
        if msg_time > hour_ago
    ]
    
    # Проверяем лимит
    if len(session['message_history']) >= max_messages_per_hour:
        return False
    
    # Добавляем текущее сообщение
    session['message_history'].append(current_time)
    return True


def create_error_response(error_type: str, details: str = "") -> Dict:
    """
    Создает стандартизированный ответ об ошибке
    
    Args:
        error_type: Тип ошибки
        details: Детали ошибки
        
    Returns:
        Dict: Ответ об ошибке
    """
    return {
        'error': True,
        'error_type': error_type,
        'message': details,
        'timestamp': datetime.now().isoformat()
    }


def validate_webhook_signature(request_body: bytes, signature: str, app_secret: str) -> bool:
    """
    Проверяет подпись webhook от WhatsApp
    
    Args:
        request_body: Тело запроса
        signature: Подпись из заголовка
        app_secret: Секрет приложения
        
    Returns:
        bool: True если подпись валидна
    """
    try:
        import hmac
        import hashlib
        
        if not signature or not app_secret:
            return False
        
        # Извлекаем подпись из заголовка
        signature_parts = signature.split('=')
        if len(signature_parts) != 2:
            return False
        
        algorithm, signature_hash = signature_parts
        
        # Вычисляем подпись
        expected_signature = hmac.new(
            app_secret.encode('utf-8'),
            request_body,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature_hash, expected_signature)
        
    except Exception as e:
        logger.error(f"Ошибка проверки подписи webhook: {e}")
        return False


def get_system_info() -> Dict:
    """
    Возвращает информацию о системе
    
    Returns:
        Dict: Информация о системе
    """
    import platform
    import psutil
    
    try:
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'memory_available': psutil.virtual_memory().available,
            'disk_usage': psutil.disk_usage('/').percent
        }
    except ImportError:
        # psutil может быть не установлен
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'python_version': platform.python_version(),
            'note': 'psutil not available for detailed system info'
        }
    except Exception as e:
        logger.error(f"Ошибка получения информации о системе: {e}")
        return {'error': str(e)} 