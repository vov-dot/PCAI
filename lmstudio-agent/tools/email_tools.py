"""
Модуль для работы с электронной почтой
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json
import os


def send_email(to: str, subject: str, body: str, cc: str = None) -> dict:
    """
    Отправляет электронное письмо.
    
    Args:
        to: Email получателя
        subject: Тема письма
        body: Текст письма
        cc: Email для копии (опционально)
    
    Returns:
        Статус отправки
    """
    # Загружаем настройки
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'settings.json')
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        return {
            "success": False,
            "error": "Файл конфигурации не найден",
            "message": "Настройте config/settings.json с параметрами SMTP"
        }
    
    email_config = config.get('email', {})
    smtp_server = email_config.get('smtp_server')
    smtp_port = email_config.get('smtp_port')
    username = email_config.get('username')
    password = email_config.get('password')
    
    if not all([smtp_server, username, password]):
        return {
            "success": False,
            "error": "SMTP настройки не конфигурированы",
            "message": "Пожалуйста, настройте параметры SMTP в config/settings.json"
        }
    
    try:
        # Создаем письмо
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = to
        msg['Subject'] = subject
        
        if cc:
            msg['Cc'] = cc
        
        # Добавляем тело письма
        msg.attach(MIMEText(body, 'plain'))
        
        # Формируем список получателей
        recipients = [to]
        if cc:
            recipients.extend(cc.split(','))
        
        # Отправляем письмо
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
        
        return {
            "success": True,
            "message": f"Письмо успешно отправлено на {to}",
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Не удалось отправить письмо"
        }


def draft_email(to: str, subject: str, body: str) -> dict:
    """
    Сохраняет черновик письма в файл (если SMTP не настроен).
    
    Args:
        to: Email получателя
        subject: Тема письма
        body: Текст письма
    
    Returns:
        Путь к файлу черновика
    """
    drafts_dir = os.path.join(os.getcwd(), 'output', 'email_drafts')
    os.makedirs(drafts_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"draft_{timestamp}.txt"
    filepath = os.path.join(drafts_dir, filename)
    
    content = f"""TO: {to}
SUBJECT: {subject}
DATE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{body}
"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return {
        "success": True,
        "message": "Черновик сохранен (SMTP не настроен)",
        "filepath": filepath
    }
