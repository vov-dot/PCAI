# mcp_server.py
import sys
import os
from mcp.server.fastmcp import FastMCP

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import base

mcp = FastMCP("AI-Action-Tools", version="1.0.0")

@mcp.tool()
def search_web(query: str, max_results: int = 5) -> str:
    """Ищет информацию в интернете. Возвращает текст с источниками.
    ИСПОЛЬЗУЙ ПЕРЕД созданием документов/таблиц, если нужны свежие данные."""
    return base.web_search(query, max_results)

@mcp.tool()
def create_google_document(content: str, title: str = "AI_Document") -> str:
    """Создает Google Doc из УЖЕ СФОРМИРОВАННОГО текста. Возвращает ссылку.
    Текст должен содержать разметку, заголовки и списки."""
    return base.create_google_document(content, title)

@mcp.tool()
def create_google_sheet(data: str, title: str = "AI_Sheet") -> str:
    """Создает Google Sheet из JSON-массива объектов или CSV.
    Пример JSON: [{"Товар": "X", "Цена": "100"}, {"Товар": "Y", "Цена": "200"}]"""
    return base.create_google_sheet(data, title)

@mcp.tool()
def get_gmail_inbox() -> str:
    """Получает краткий список последних писем (тема, отправитель) из Gmail."""
    return base.get_gmail_inbox()

@mcp.tool()
def read_gmail_full(index: int = 1) -> str:
    """Читает полное содержимое конкретного письма.
    index: 1 - самое последнее, 2 - предпоследнее и т.д. (макс 10)."""
    return base.get_gmail_full(index)

@mcp.tool()
def send_gmail_email(to: str, subject: str, body: str) -> str:
    """Отправляет email. Требует: адрес, тему и ПОЛНОЕ тело письма (сгенерированное заранее)."""
    return base.send_gmail_email(to, subject, body)

if __name__ == "__main__":
    mcp.run()
