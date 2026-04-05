import os
import json
import re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError 

SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/spreadsheets'
]

CREDENTIALS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "credentials.json")
TOKEN_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "token.json")

def get_creds():
    """Получает или обновляет OAuth2 токены."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w', encoding='utf-8') as token:
            token.write(creds.to_json())
    return creds

def create_google_doc(content: str, title: str = "AI Document") -> str:
    """Создаёт реальный Google Doc и возвращает ссылку."""
    try:
        creds = get_creds()
        service = build('docs', 'v1', credentials=creds)

        # Создание документа
        doc = service.documents().create(body={'title': title}).execute()
        doc_id = doc.get('documentId')

        # Вставка контента
        if content.strip():
            requests = [{
                'insertText': {
                    'location': {'index': 1},
                    'text': content
                }
            }]
            service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()

        return f"https://docs.google.com/document/d/{doc_id}/edit"
    except HttpError as err:
        raise RuntimeError(f"Google Docs API Error: {err}")

def _parse_table_data(text: str) -> list:
    """Парсит ответ LLM в 2D массив для Sheets."""
    text = text.strip()
    # Убираем markdown блоки если LLM их добавил
    text = re.sub(r'```(?:json|csv|table)?\n?', '', text).strip()
    text = re.sub(r'```$', '', text).strip()

    if text.startswith('['):
        try:
            data = json.loads(text)
            if isinstance(data, list) and data:
                if isinstance(data[0], dict):
                    headers = list(data[0].keys())
                    return [headers] + [[row.get(h, '') for h in headers] for row in data]
                return data
        except: pass

    # Fallback: построчный парсинг
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    result = []
    for line in lines:
        if ',' in line:
            result.append([c.strip() for c in line.split(',')])
        elif ';' in line:
            result.append([c.strip() for c in line.split(';')])
        else:
            result.append([line.strip()])
    return result

def create_google_sheet(data_text: str, title: str = "AI_Sheet") -> str:
    """Создаёт реальную Google Sheet и заполняет её."""
    try:
        creds = get_creds()
        service = build('sheets', 'v4', credentials=creds)

        # Создание таблицы
        spreadsheet = service.spreadsheets().create(
            body={'properties': {'title': title}}
        ).execute()
        sheet_id = spreadsheet.get('spreadsheetId')

        # Парсинг данных из ответа LLM
        text = data_text.strip()
        text = re.sub(r'```(?:json|csv|table)?\n?', '', text).strip()
        text = re.sub(r'```$', '', text).strip()

        values = []
        # Попытка распарсить JSON
        if text.startswith('['):
            try:
                data = json.loads(text)
                if isinstance(data, list) and data:
                    if isinstance(data[0], dict):
                        headers = list(data[0].keys())
                        values.append(headers)
                        for row in data:
                            values.append([str(row.get(h, '')) for h in headers])
                    else:
                        for row in data:
                            if isinstance(row, list):
                                values.append([str(c) for c in row])
            except Exception:
                pass

        # Fallback: CSV / разделители
        if not values:
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            for line in lines:
                if ',' in line:
                    values.append([c.strip() for c in line.split(',')])
                elif ';' in line:
                    values.append([c.strip() for c in line.split(';')])
                elif '%' in line:
                    values.append([c.strip() for c in line.split('%')])
                else:
                    values.append([line.strip()])

        if values:
            service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range='A1',  
                valueInputOption='RAW',
                body={'values': values}
            ).execute()

        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"

    except HttpError as err:
        error_content = err.content.decode('utf-8') if isinstance(err.content, bytes) else str(err.content)
        raise RuntimeError(f"Google Sheets API Error: {err}\nDetails: {error_content}")