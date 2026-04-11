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

# Маппинг имен инструментов на функции из base.py
TOOL_FUNCTIONS = {
    "search_web": base.web_search,
    "create_google_document": base.create_google_document,
    "create_google_sheet": base.create_google_sheet,
    "get_gmail_inbox": base.get_gmail_inbox,
    "read_gmail_full": base.get_gmail_full,
    "send_gmail_email": base.send_gmail_email
}

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
    messages = [{"role": "user", "content": user_message}]
    if history.strip():
        messages.insert(0, {"role": "system", "content": f"Предыдущий диалог:\n{history.strip()}"})
        
    for _ in range(max_turns):
        try:
            model = get_model()
            response = model.respond(messages, tools=TOOLS, config={"temperature": 0.7})
        except Exception as e:
            return f"❌ Ошибка подключения к LLM: {str(e)}"
            
        # Проверяем, запросила ли модель инструмент
        if hasattr(response, 'tool_calls') and response.tool_calls:
            # Сохраняем сообщение с запросом инструмента
            messages.append(response.message)
            
            for tool_call in response.tool_calls:
                logging.info(f"🛠️ Вызов: {tool_call.function.name}")
                result = execute_tool_call(tool_call)
                
                # Возвращаем результат в контекст
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
        else:
            # Модель вернула финальный текстовый ответ
            return str(response.text if hasattr(response, 'text') else response)
            
    return "⚠️ Достигнут лимит шагов выполнения инструментов. Попробуйте переформулировать запрос."

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
