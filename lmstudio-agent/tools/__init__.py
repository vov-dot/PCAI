"""
Модуль инициализации всех инструментов
"""
import sys
import os

# Добавляем путь к инструментам
sys.path.insert(0, os.path.dirname(__file__))

from tools.document_tools import (
    create_word_document,
    create_excel_table,
    append_to_word_document,
    read_excel_file
)

from tools.email_tools import (
    send_email,
    draft_email
)

from tools.price_tools import (
    search_product_prices,
    compare_products,
    get_price_history
)

from tools.utils_tools import (
    get_current_datetime,
    get_system_info,
    calculate,
    create_reminder,
    list_files,
    read_file
)

from tools.tool_registry import TOOLS_CONFIG, build_tool_defs

# Словарь всех доступных функций
ALL_FUNCTIONS = {
    # Документы
    "create_word_document": create_word_document,
    "create_excel_table": create_excel_table,
    "append_to_word_document": append_to_word_document,
    "read_excel_file": read_excel_file,
    
    # Почта
    "send_email": send_email,
    "draft_email": draft_email,
    
    # Цены
    "search_product_prices": search_product_prices,
    "compare_products": compare_products,
    "get_price_history": get_price_history,
    
    # Утилиты
    "get_current_datetime": get_current_datetime,
    "get_system_info": get_system_info,
    "calculate": calculate,
    "create_reminder": create_reminder,
    "list_files": list_files,
    "read_file": read_file
}


def get_all_tools():
    """
    Возвращает все инструменты в формате lmstudio с реализациями.
    
    Returns:
        Список объектов ToolFunctionDef с привязанными функциями
    """
    return build_tool_defs(TOOLS_CONFIG, ALL_FUNCTIONS)


def get_function(name: str):
    """
    Возвращает функцию по имени.
    
    Args:
        name: Имя функции
    
    Returns:
        Функция или None если не найдена
    """
    return ALL_FUNCTIONS.get(name)


def get_all_function_names():
    """
    Возвращает список имен всех доступных функций.
    
    Returns:
        Список имен функций
    """
    return list(ALL_FUNCTIONS.keys())
