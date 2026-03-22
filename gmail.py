import os
import pickle
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request # type: ignore
from google.oauth2.credentials import Credentials # type: ignore
from google_auth_oauthlib.flow import InstalledAppFlow # type: ignore
from googleapiclient.discovery import build # type: ignore

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

class SimpleGmail:
    def __init__(self, credentials_file="..credentials.json"):

        self.service = self._authenticate(credentials_file)
        print("✅ Подключено к Gmail")
    
    def _authenticate(self, credentials_file):
        creds = None
        
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        return build('gmail', 'v1', credentials=creds)
    
    def get_last_10_emails(self):
        try:
            results = self.service.users().messages().list(
                userId='me', 
                maxResults=10,
                q='in:inbox'
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for msg in messages:
                msg_data = self.service.users().messages().get(
                    userId='me', 
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['Subject', 'From', 'Date']
                ).execute()
                
                # Извлекаем заголовки
                headers = msg_data['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Без темы')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Неизвестно')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Дата неизвестна')
                
                emails.append({
                    'id': msg['id'],
                    'subject': subject,
                    'sender': sender,
                    'date': date,
                    'snippet': msg_data['snippet']
                })
            
            return emails
            
        except Exception as e:
            print(f"❌ Ошибка получения писем: {e}")
            return []
    
    def read_full_email(self, email_id):
        try:
            msg = self.service.users().messages().get(
                userId='me', 
                id=email_id,
                format='full'
            ).execute()
            
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Без темы')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Неизвестно')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Дата неизвестна')
            
            body = self._get_email_body(msg)
            
            return {
                'id': email_id,
                'subject': subject,
                'sender': sender,
                'date': date,
                'snippet': msg['snippet'],
                'body': body
            }
            
        except Exception as e:
            print(f"❌ Ошибка чтения письма: {e}")
            return None
    
    def _get_email_body(self, msg):
        try:
            if 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'].get('data', '')
                        if data:
                            return base64.urlsafe_b64decode(data).decode('utf-8')
            else:
                data = msg['payload']['body'].get('data', '')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8')
        except:
            pass
        return " [Текст письма не найден]"
    
    def send_email(self, to, subject, body):
        try:
            message = MIMEText(body, 'plain', 'utf-8')
            message['to'] = to
            message['subject'] = subject
            
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()
            
            print(f"✅ Письмо отправлено: {subject}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка отправки: {e}")
            return False


def start(task,num=1, to=None,subject=None,body=None):
    gmail = SimpleGmail("..credentials.json")
    
    emails = gmail.get_last_10_emails()

    if task == 'late':
        result = ""
        for i, email in enumerate(emails, 1):
            result += f"{i}. {email['subject']} - {email['sender']}\n"
        
        return result
        
    if task == 'full':
        num -= 1
        full = gmail.read_full_email(emails[num]['id'])
        if full:
            return f"Тема: {full['subject']}\nОт: {full['sender']}\nТекст: {full['body']}"
    
    if task == 'email':
        gmail.send_email(to=to,subject=subject,body=body)
    

'''if __name__ == '__main__':
    print(start(num=int(input()),task='full'))'''