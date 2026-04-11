# app.py
from flask import Flask, render_template, request, jsonify
import logging
import json
import sys
import os
import lmstudio as lms

# Добавляем корень проекта в пути
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import base

app = Flask(__name__, static_folder="static", template_folder="templates")
logging.basicConfig(level=logging.INFO)

# Инициализация модели будет выполнена при первом запросе
_model = None
_model_name = "google/gemma-3-4b"

def get_model():
    """Ленивая инициализация модели."""
    global _model
    if _model is None:
        _model = lms.llm(_model_name)
    return _model

# 📜 Схемы инструментов для LLM (идентичны MCP-схеме)
TOOLS = [
    {
        "name": "search_web",
        "description": "Ищет актуальную информацию через DuckDuckGo. Используй ПЕРЕД созданием документов/таблиц, если нужны свежие данные.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Текст поискового запроса"},
                "max_results": {"type": "integer", "description": "Максимум результатов (по умолчанию 5)", "default": 5}
            },
            "required": ["query"]
        }
    },
    {
        "name": "create_google_document",
        "description": "Создает Google Doc из УЖЕ СФОРМИРОВАННОГО текста. Возвращает ссылку.",
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Готовый текст документа с разметкой"},
                "title": {"type": "string", "description": "Название документа", "default": "AI_Document"}
            },
            "required": ["content"]
        }
    },
    {
        "name": "create_google_sheet",
        "description": "Создает Google Sheet из JSON-массива объектов или CSV.",
        "input_schema": {
            "type": "object",
            "properties": {
                "data": {"type": "string", "description": "Данные в формате JSON массива объектов или CSV"},
                "title": {"type": "string", "description": "Название таблицы", "default": "AI_Sheet"}
            },
            "required": ["data"]
        }
    },
    {
        "name": "get_gmail_inbox",
        "description": "Получает краткий список последних писем из Gmail (тема, отправитель).",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "read_gmail_full",
        "description": "Читает полное содержимое конкретного письма.",
        "input_schema": {
            "type": "object",
            "properties": {
                "index": {"type": "integer", "description": "Индекс письма (1 = последнее, 2 = предпоследнее, макс 10)", "default": 1}
            }
        }
    },
    {
        "name": "send_gmail_email",
        "description": "Отправляет email через Gmail. Требует адрес, тему и готовое тело письма.",
        "input_schema": {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Email получателя"},
                "subject": {"type": "string", "description": "Тема письма"},
                "body": {"type": "string", "description": "Текст письма"}
            },
            "required": ["to", "subject", "body"]
        }
    }
]

# Маппинг имен инструментов на функции из base.py (для внутреннего использования)
TOOL_FUNCTION_MAP = {
    "search_web": base.web_search,
    "create_google_document": base.create_google_document,
    "create_google_sheet": base.create_google_sheet,
    "get_gmail_inbox": base.get_gmail_inbox,
    "read_gmail_full": base.get_gmail_full,
    "send_gmail_email": base.send_gmail_email
}

# Преобразуем схемы TOOLS в формат ToolFunctionDef для lmstudio
def build_tool_defs():
    """Создает список ToolFunctionDef из схем TOOLS и функций TOOL_FUNCTION_MAP."""
    tool_defs = []
    for tool in TOOLS:
        func = TOOL_FUNCTION_MAP.get(tool["name"])
        if func is None:
            logging.warning(f"Функция для инструмента {tool['name']} не найдена")
            continue
        
        # Преобразуем input_schema в параметры в формате ToolParamDefDict
        params = {}
        properties = tool["input_schema"].get("properties", {})
        required = tool["input_schema"].get("required", [])
        
        for param_name, param_def in properties.items():
            param_type = param_def.get("type", "string")
            type_map = {
                "string": str,
                "integer": int,
                "number": float,
                "boolean": bool,
                "array": list,
                "object": dict
            }
            python_type = type_map.get(param_type, str)
            
            # Создаем ToolParamDefDict с правильными полями
            param_def_dict = lms.json_api.ToolParamDefDict[python_type]()
            param_def_dict["type"] = python_type
            param_def_dict["description"] = param_def.get("description", "")
            if "default" in param_def:
                param_def_dict["default"] = param_def["default"]
            
            params[param_name] = param_def_dict
        
        tool_defs.append(lms.ToolFunctionDef(
            name=tool["name"],
            description=tool["description"],
            parameters=params,
            implementation=func
        ))
    
    return tool_defs

TOOL_DEFS = build_tool_defs()

def execute_tool_call(tool_call):
    """Выполняет инструмент и возвращает результат."""
    func_name = tool_call.function.name
    try:
        args = json.loads(tool_call.function.arguments)
    except json.JSONDecodeError:
        return "❌ Ошибка: некорректные аргументы инструмента."
        
    if func_name not in TOOL_FUNCTIONS:
        return f"❌ Ошибка: неизвестный инструмент {func_name}"
        
    try:
        result = TOOL_FUNCTIONS[func_name](**args)
        return str(result)
    except Exception as e:
        logging.error(f"Ошибка выполнения {func_name}: {e}")
        return f"❌ Ошибка выполнения инструмента: {str(e)}"

def run_tool_loop(user_message: str, history: str = "", max_turns: int = 6) -> str:
    """Автоматический цикл: LLM → Выбор инструмента → Выполнение → Возврат ответа."""
    # Формируем начальное сообщение
    chat = lms.Chat()
    chat.add_user_message(user_message)
    if history.strip():
        chat.add_system_prompt(f"Предыдущий диалог:\n{history.strip()}")
        
    try:
        model = get_model()
        # Используем метод act() для работы с инструментами
        result = model.act(
            chat,
            tools=TOOL_DEFS,  # Передаем ToolFunctionDef объекты
            max_prediction_rounds=max_turns,
            config={"temperature": 0.7}
        )
        return str(result.response.text if hasattr(result.response, 'text') else result.response)
    except Exception as e:
        return f"❌ Ошибка подключения к LLM: {str(e)}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def api_chat():
    try:
        data = request.get_json(force=True, silent=True) or {}
        message = data.get("message", "").strip()
        history = data.get("history", "")
        
        if not message:
            return jsonify({"response": "⚠️ Введите сообщение"}), 400
            
        # Запускаем единый цикл с автоматическим выбором инструментов
        response = run_tool_loop(message, history)
        return jsonify({"response": response})
        
    except Exception as e:
        logging.exception("Критическая ошибка в /api/chat")
        return jsonify({"response": f"❌ Внутренняя ошибка сервера: {str(e)}"}), 500

if __name__ == "__main__":
    print("🚀 Запуск веб-интерфейса на http://127.0.0.1:5000")
    app.run(debug=True, host="127.0.0.1", port=5000)
