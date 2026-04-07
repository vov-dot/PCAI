import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from back import ddg, gmail
from back.google_api import create_google_doc, create_google_sheet

def web_search(query: str, max_results: int = 5) -> str:
    """Прямой поиск через DuckDuckGo. Возвращает отформатированный текст страниц."""
    return ddg.search(query, max_results=max_results)

def create_google_document(content: str, title: str = "AI_Document") -> str:
    """Создает Google Doc из готового текста. Возвращает ссылку."""
    return create_google_doc(content, title)

def create_google_sheet(data: str, title: str = "AI_Sheet") -> str:
    """Создает Google Sheet из JSON-массива или CSV. Возвращает ссылку."""
    return create_google_sheet(data, title)

def get_gmail_inbox() -> str:
    """Возвращает заголовки последних писем из Gmail (тема, отправитель)."""
    return gmail.start(task='late')

def get_gmail_full(index: int = 1) -> str:
    """Возвращает полное содержание письма. index: 1 = последнее, 2 = предпоследнее (макс 10)."""
    return gmail.start(task='full', num=index)

def send_gmail_email(to: str, subject: str, body: str) -> str:
    """Отправляет email через Gmail. Возвращает статус отправки."""
    gmail.start(task='email', to=to, subject=subject, body=body)
    return f"✅ Письмо успешно отправлено на {to}\nТема: {subject}"
