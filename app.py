from flask import Flask, render_template, request, jsonify
from base import create_search_response, document, table, gmail_action

app = Flask(__name__, static_folder="static", template_folder="templates")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/search_prompt", methods=["POST"])
def api_search_prompt():
    data = request.json or {}
    prompt = data.get("prompt", "")
    out = create_search_response(prompt)
    return jsonify({"result": out})

@app.route("/api/document", methods=["POST"])
def api_document():
    data = request.json or {}
    prompt = data.get("prompt", "")
    out = document(prompt)
    return jsonify({"result": out})

@app.route("/api/table", methods=["POST"])
def api_table():
    data = request.json or {}
    prompt = data.get("prompt", "")
    out = table(prompt)
    return jsonify({"result": out})

@app.route("/api/gmail", methods=["POST"])
def api_gmail():
    data = request.json or {}
    prompt = data.get("prompt", "")
    g_task = data.get("g_task")
    extra = data.get("extra", {})
    out = gmail_action(prompt, g_task, extra)
    return jsonify({"result": out})

if __name__ == "__main__":
    app.run(debug=True)
