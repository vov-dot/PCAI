from flask import Flask, render_template, request, jsonify
import logging
from base import create_search_response, document, table, gmail_action
from back.todo import TodoManager


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


todo_manager = TodoManager("data/tasks.json")


@app.before_request
def log_request_info():
    logger.info(f"{request.method} {request.path} | IP: {request.remote_addr}")

# === Главная страница ===
@app.route("/")
def index():
    return render_template("index.html")

# ==================== to-do API ====================

@app.route("/api/todo/tasks", methods=["GET"])
def api_get_tasks():
    filter_status = request.args.get("status", "all")
    
    if filter_status == "pending":
        tasks = todo_manager.get_pending_tasks()
    elif filter_status == "completed":
        tasks = todo_manager.get_completed_tasks()
    else:
        tasks = todo_manager.get_all_tasks()
    
    return jsonify({
        "tasks": [t.to_dict() for t in tasks],
        "stats": todo_manager.get_statistics()
    })

@app.route("/api/todo/tasks", methods=["POST"])
def api_add_task():
    data = request.get_json(force=True, silent=True) or {}
    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    priority = data.get("priority", "medium")
    
    if not title:
        return jsonify({"error": "Название задачи обязательно"}), 400
    
    task = todo_manager.add_task(title, description, priority)
    logger.info(f"Task added: {task.id} - {task.title}")
    return jsonify({"task": task.to_dict(), "message": "Задача добавлена"}), 201

@app.route("/api/todo/tasks/<int:task_id>", methods=["GET"])
def api_get_task(task_id):
    task = todo_manager.get_task(task_id)
    if not task:
        return jsonify({"error": "Задача не найдена"}), 404
    return jsonify({"task": task.to_dict()})

@app.route("/api/todo/tasks/<int:task_id>", methods=["PUT"])
def api_update_task(task_id):
    data = request.get_json(force=True, silent=True) or {}
    completed = data.get("completed", True)
    
    if completed:
        task = todo_manager.complete_task(task_id)
    else:
        task = todo_manager.uncomplete_task(task_id)
    
    if not task:
        return jsonify({"error": "Задача не найдена"}), 404
    
    return jsonify({"task": task.to_dict(), "message": "Статус обновлён"})

@app.route("/api/todo/tasks/<int:task_id>", methods=["DELETE"])
def api_delete_task(task_id):
    if todo_manager.remove_task(task_id):
        logger.info(f"Task deleted: {task_id}")
        return jsonify({"message": "Задача удалена"})
    return jsonify({"error": "Задача не найдена"}), 404

@app.route("/api/todo/stats", methods=["GET"])
def api_get_stats():
    return jsonify(todo_manager.get_statistics())

@app.route("/api/todo/search", methods=["GET"])
def api_search_tasks():
    query = request.args.get("q", "")
    if not query:
        return jsonify({"tasks": [], "message": "Введите поисковый запрос"}), 400
    
    tasks = todo_manager.search_tasks(query)
    return jsonify({"tasks": [t.to_dict() for t in tasks], "count": len(tasks)})

@app.route("/api/todo/clear-completed", methods=["POST"])
def api_clear_completed():
    removed = todo_manager.clear_completed()
    return jsonify({"message": f"Удалено {removed} завершённых задач", "removed": removed})

# ==================== AI API ====================

@app.route("/api/document", methods=["POST"])
def api_document():
    try:
        data = request.get_json(force=True, silent=True) or {}
        prompt = data.get("prompt", "").strip()
        if not prompt:
            return jsonify({"result": "Введите тему документа"}), 400
        logger.info(f"Document prompt: {prompt[:100]}...")
        out = document(prompt)
        return jsonify({"result": out})
    except Exception as e:
        logger.error(f"Document error: {e}", exc_info=True)
        return jsonify({"result": f"Ошибка: {str(e)}"}), 500

@app.route("/api/table", methods=["POST"])
def api_table():
    try:
        data = request.get_json(force=True, silent=True) or {}
        prompt = data.get("prompt", "").strip()
        if not prompt:
            return jsonify({"result": "Опишите данные для таблицы"}), 400
        logger.info(f"Table prompt: {prompt[:100]}...")
        out = table(prompt)
        return jsonify({"result": out})
    except Exception as e:
        logger.error(f"Table error: {e}", exc_info=True)
        return jsonify({"result": f"Ошибка: {str(e)}"}), 500

@app.route("/api/gmail", methods=["POST"])
def api_gmail():
    try:
        data = request.get_json(force=True, silent=True) or {}
        g_task = data.get("g_task")
        extra = data.get("extra", {}) or {}
        
        out = gmail_action(g_task, extra)
        return jsonify({"result": out})
    except Exception as e:
        logger.error(f"Gmail error: {e}", exc_info=True)
        return jsonify({"result": f"Ошибка: {str(e)}"}), 500

# === Запуск ===
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
