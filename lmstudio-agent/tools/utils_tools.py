"""
Дополнительные утилиты для агента
"""
import os
import json
from datetime import datetime
from typing import List, Dict


def get_current_datetime() -> str:
    """
    Возвращает текущую дату и время.
    
    Returns:
        Строка с текущей датой и временем
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def get_system_info() -> Dict:
    """
    Возвращает информацию о системе.
    
    Returns:
        Словарь с информацией о системе
    """
    import platform
    
    return {
        "platform": platform.system(),
        "platform_release": platform.release(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "hostname": platform.node(),
        "python_version": platform.python_version(),
        "current_directory": os.getcwd()
    }


def calculate(expression: str) -> Dict:
    """
    Вычисляет математическое выражение.
    
    Args:
        expression: Математическое выражение в виде строки
    
    Returns:
        Результат вычисления
    """
    try:
        # Безопасное вычисление выражения
        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in expression):
            return {
                "success": False,
                "error": "Недопустимые символы в выражении"
            }
        
        result = eval(expression)
        
        return {
            "success": True,
            "expression": expression,
            "result": result,
            "timestamp": get_current_datetime()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "expression": expression
        }


def create_reminder(title: str, description: str, priority: str = "normal") -> Dict:
    """
    Создает напоминание (сохраняет в файл).
    
    Args:
        title: Заголовок напоминания
        description: Описание напоминания
        priority: Приоритет (low, normal, high)
    
    Returns:
        Информация о созданном напоминании
    """
    reminders_dir = os.path.join(os.getcwd(), 'output', 'reminders')
    os.makedirs(reminders_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"reminder_{timestamp}.json"
    filepath = os.path.join(reminders_dir, filename)
    
    reminder = {
        "title": title,
        "description": description,
        "priority": priority,
        "created_at": get_current_datetime(),
        "status": "pending"
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(reminder, f, indent=2, ensure_ascii=False)
    
    return {
        "success": True,
        "message": "Напоминание создано",
        "filepath": filepath,
        "reminder": reminder
    }


def list_files(directory: str = "output") -> List[str]:
    """
    Список файлов в директории.
    
    Args:
        directory: Путь к директории
    
    Returns:
        Список имен файлов
    """
    full_path = os.path.join(os.getcwd(), directory)
    
    if not os.path.exists(full_path):
        return [f"Директория {directory} не найдена"]
    
    files = []
    for item in os.listdir(full_path):
        item_path = os.path.join(full_path, item)
        if os.path.isfile(item_path):
            files.append(item)
        elif os.path.isdir(item_path):
            files.append(f"[DIR] {item}")
            # Рекурсивно列出 файлы в поддиректориях
            for subitem in list_files(os.path.join(directory, item)):
                files.append(f"  - {subitem}")
    
    return files


def read_file(filename: str) -> Dict:
    """
    Читает содержимое файла.
    
    Args:
        filename: Имя файла для чтения
    
    Returns:
        Содержимое файла или ошибка
    """
    filepath = os.path.join(os.getcwd(), 'output', filename)
    
    if not os.path.exists(filepath):
        return {
            "success": False,
            "error": f"Файл {filepath} не найден"
        }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "success": True,
            "filename": filename,
            "content": content,
            "size_bytes": len(content.encode('utf-8'))
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
