from flask import Flask, render_template, request, jsonify
import logging
import os
from base import chat, chat_search, document, document_no_search, table, table_no_search, gmail_action
app = Flask(__name__, static_folder="static", template_folder="templates")
logging.basicConfig(level=logging.INFO)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def api_chat():
    try:
        data = request.get_json(force=True, silent=True) or {}
        message = data.get("message", "").strip()
        history = data.get("history", "")
        use_search = data.get("search", False)

        if not message:
            return jsonify({"response": "⚠️ Введите сообщение"}), 400

        response = chat_search(message, history) if use_search else chat(message, history)
        return jsonify({"response": response})
    except Exception as e:
        logging.exception("Ошибка чата")
        return jsonify({"response": f"❌ Ошибка: {str(e)}"}), 500

@app.route("/api/document", methods=["POST"])
def api_document():
    data = request.get_json(force=True, silent=True) or {}
    prompt = data.get("prompt", "").strip()
    if not prompt: return jsonify({"result": "⚠️ Введите тему документа"}), 400
    try:
        return jsonify({"result": document(prompt)})
    except Exception as e:
        return jsonify({"result": f"❌ Ошибка: {str(e)}"}), 500

@app.route("/api/document_no_search", methods=["POST"])
def api_document_no_search():
    data = request.get_json(force=True, silent=True) or {}
    prompt = data.get("prompt", "").strip()
    if not prompt: return jsonify({"result": "⚠️ Введите тему документа"}), 400
    try:
        return jsonify({"result": document_no_search(prompt)})
    except Exception as e:
        return jsonify({"result": f"❌ Ошибка: {str(e)}"}), 500

@app.route("/api/table", methods=["POST"])
def api_table():
    data = request.get_json(force=True, silent=True) or {}
    prompt = data.get("prompt", "").strip()
    if not prompt: return jsonify({"result": "⚠️ Опишите данные таблицы"}), 400
    try:
        return jsonify({"result": table(prompt)})
    except Exception as e:
        return jsonify({"result": f"❌ Ошибка: {str(e)}"}), 500

@app.route("/api/table_no_search", methods=["POST"])
def api_table_no_search():
    data = request.get_json(force=True, silent=True) or {}
    prompt = data.get("prompt", "").strip()
    if not prompt: return jsonify({"result": "⚠️ Опишите данные таблицы"}), 400
    try:
        return jsonify({"result": table_no_search(prompt)})
    except Exception as e:
        return jsonify({"result": f"❌ Ошибка: {str(e)}"}), 500


@app.route("/api/gmail", methods=["POST"])
def api_gmail():
    try:
        data = request.get_json(force=True, silent=True) or {}
        g_task = data.get("g_task", "").strip()
        extra = data.get("extra", {}) or {}
        if not g_task:
            return jsonify({"result": "⚠️ Не указана задача Gmail"}), 400
        out = gmail_action(g_task, extra)
        return jsonify({"result": out})
    except Exception as e:
        logging.exception("Ошибка в /api/gmail")
        return jsonify({"result": f"❌ Ошибка Gmail: {str(e)}"}), 500




@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

if __name__ == "__main__":
    print("🚀 Запуск сервера на http://127.0.0.1:5000")
    app.run(debug=True, host="127.0.0.1", port=5000)
