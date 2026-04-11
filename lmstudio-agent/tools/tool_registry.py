"""
Модуль регистрации инструментов для LMStudio
Создает правильные определения инструментов совместимые с lmstudio 1.5.0
"""
from typing import Mapping, Union, Callable, Any
from lmstudio.json_api import ToolFunctionDef, ToolParamDefDict


def build_tool_defs(tools_config: list, functions_map: dict) -> list:
    """
    Преобразует конфигурацию инструментов в формат lmstudio.ToolFunctionDef.
    
    Args:
        tools_config: Список словарей с конфигурацией инструментов
        functions_map: Словарь с функциями для реализации
    
    Returns:
        Список объектов ToolFunctionDef
    """
    tool_defs = []
    
    for tool in tools_config:
        # Создаем параметры в правильном формате - словарь str -> ToolParamDefDict
        params: Mapping[str, Union[type[Any], ToolParamDefDict[Any]]] = {}
        
        for param in tool.get('parameters', []):
            param_type = param['type']
            
            # Маппинг типов JSON Schema в Python типы
            type_mapping = {
                'string': str,
                'integer': int,
                'number': float,
                'boolean': bool,
                'array': list,
                'object': dict,
                'null': type(None)
            }
            
            python_type = type_mapping.get(param_type, str)
            
            # Создаем описание параметра
            param_def = ToolParamDefDict(
                type=python_type,
                description=param.get('description', ''),
                default=param.get('default')
            )
            
            params[param['name']] = param_def
        
        # Получаем реализацию функции
        implementation = functions_map.get(tool['name'])
        
        if not implementation:
            print(f"⚠️ Предупреждение: функция {tool['name']} не найдена")
            continue
        
        # Создаем определение функции с реализацией
        func_def = ToolFunctionDef(
            name=tool['name'],
            description=tool.get('description', ''),
            parameters=params,
            implementation=implementation
        )
        
        tool_defs.append(func_def)
    
    return tool_defs


# Конфигурация всех доступных инструментов
TOOLS_CONFIG = [
    # Документы
    {
        "name": "create_word_document",
        "description": "Создает новый Word документ с заголовком и содержанием",
        "parameters": [
            {"name": "filename", "type": "string", "description": "Имя файла (без расширения .docx)"},
            {"name": "title", "type": "string", "description": "Заголовок документа"},
            {"name": "content", "type": "string", "description": "Основное содержание документа"}
        ]
    },
    {
        "name": "create_excel_table",
        "description": "Создает Excel таблицу из данных",
        "parameters": [
            {"name": "filename", "type": "string", "description": "Имя файла (без расширения .xlsx)"},
            {"name": "data", "type": "array", "description": "Список строк данных (каждая строка - список значений)"},
            {"name": "columns", "type": "array", "description": "Список названий колонок (опционально)", "default": None}
        ]
    },
    {
        "name": "append_to_word_document",
        "description": "Добавляет текст в существующий Word документ",
        "parameters": [
            {"name": "filename", "type": "string", "description": "Имя файла документа"},
            {"name": "text", "type": "string", "description": "Текст для добавления"}
        ]
    },
    {
        "name": "read_excel_file",
        "description": "Читает Excel файл и возвращает данные",
        "parameters": [
            {"name": "filename", "type": "string", "description": "Имя файла для чтения"}
        ]
    },
    
    # Почта
    {
        "name": "send_email",
        "description": "Отправляет электронное письмо",
        "parameters": [
            {"name": "to", "type": "string", "description": "Email получателя"},
            {"name": "subject", "type": "string", "description": "Тема письма"},
            {"name": "body", "type": "string", "description": "Текст письма"},
            {"name": "cc", "type": "string", "description": "Email для копии (опционально)", "default": None}
        ]
    },
    {
        "name": "draft_email",
        "description": "Сохраняет черновик письма в файл (если SMTP не настроен)",
        "parameters": [
            {"name": "to", "type": "string", "description": "Email получателя"},
            {"name": "subject", "type": "string", "description": "Тема письма"},
            {"name": "body", "type": "string", "description": "Текст письма"}
        ]
    },
    
    # Цены
    {
        "name": "search_product_prices",
        "description": "Ищет цены на товар в различных магазинах",
        "parameters": [
            {"name": "product_name", "type": "string", "description": "Название товара для поиска"}
        ]
    },
    {
        "name": "compare_products",
        "description": "Сравнивает цены на несколько товаров",
        "parameters": [
            {"name": "products", "type": "array", "description": "Список названий товаров для сравнения"}
        ]
    },
    {
        "name": "get_price_history",
        "description": "Симулирует историю изменения цен на товар за последние 30 дней",
        "parameters": [
            {"name": "product_name", "type": "string", "description": "Название товара"}
        ]
    },
    
    # Утилиты
    {
        "name": "get_current_datetime",
        "description": "Возвращает текущую дату и время",
        "parameters": []
    },
    {
        "name": "get_system_info",
        "description": "Возвращает информацию о системе",
        "parameters": []
    },
    {
        "name": "calculate",
        "description": "Вычисляет математическое выражение",
        "parameters": [
            {"name": "expression", "type": "string", "description": "Математическое выражение в виде строки"}
        ]
    },
    {
        "name": "create_reminder",
        "description": "Создает напоминание (сохраняет в файл)",
        "parameters": [
            {"name": "title", "type": "string", "description": "Заголовок напоминания"},
            {"name": "description", "type": "string", "description": "Описание напоминания"},
            {"name": "priority", "type": "string", "description": "Приоритет (low, normal, high)", "default": "normal"}
        ]
    },
    {
        "name": "list_files",
        "description": "Список файлов в директории",
        "parameters": [
            {"name": "directory", "type": "string", "description": "Путь к директории", "default": "output"}
        ]
    },
    {
        "name": "read_file",
        "description": "Читает содержимое файла",
        "parameters": [
            {"name": "filename", "type": "string", "description": "Имя файла для чтения"}
        ]
    }
]
