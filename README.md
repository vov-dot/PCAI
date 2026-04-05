# PCAI — Flask + LM Studio + Google API

> Полноценный чат-ассистент с поддержкой веб-поиска, созданием документов в Google Docs/Sheets и управлением Gmail.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 📋 Оглавление
- [Возможности](#-возможности)
- [Технологии](#-технологии)
- [Структура проекта](#-структура-проекта)
- [Установка](#-установка)
- [Настройка Google Cloud](#-настройка-google-cloud)
- [Настройка LM Studio](#-настройка-lm-studio)
- [Запуск](#-запуск)
- [Использование](#-использование)
- [API Endpoints](#-api-endpoints)
- [Устранение неполадок](#-устранение-неполадок)
- [Лицензия](#-лицензия)

---

## ✨ Возможности

### 💬 Чат с нейросетью
- Подключение к локальным моделям через **LM Studio** (Qwen, Gemma, Llama и др.)
- Сохранение истории диалогов в браузере
- Поддержка **Markdown**: заголовки, списки, код, таблицы, ссылки
- Подсветка синтаксиса кода (highlight.js)

### 🔍 Веб-поиск
- Интеграция с **DuckDuckGo** через `ddgs`

### 📄 Google Docs / 📊 Google Sheets
- Создание реальных документов через **официальный Google API**
- OAuth2 авторизация с сохранением токена
- Автоматическое форматирование ответа LLM в таблицу (JSON/CSV/разделители)
- Прямые ссылки на созданные файлы в вашем Google Диске

### 📧 Управление Gmail
- 📥 Просмотр последних 10 писем
- 📖 Чтение полного содержимого конкретного письма
- ✉️ Написание и отправка писем через нейросеть
- Полная авторизация через Google OAuth2

---

## 🛠 Технологии

| Компонент | Технология |
|-----------|-----------|
| Бэкенд | Python 3.10+, Flask 2.3+ |
| Нейросеть | LM Studio (локальный сервер) |
| Поиск | DuckDuckGo Search (`ddgs`), `aiohttp`, `BeautifulSoup4` |
| Google API | `google-api-python-client`, `google-auth`, `google-auth-oauthlib` |
| Фронтенд | HTML5, CSS3, Vanilla JS |
| Markdown | `marked.js`, `DOMPurify`, `highlight.js` |
| Хранение | `localStorage` (история чатов), `token.pickle` (OAuth) |

---

## 📁 Структура проекта

```
PCAI/
│
├── app.py                      # Flask сервер, API endpoints
├── base.py                     # Логика AI: chat, search, docs, sheets, gmail
├── requirements.txt            # Зависимости Python
│
├── back/                       # Модули бэкенда
│   ├── __init__.py
│   ├── ddg.py                  # Поиск + парсинг веб-страниц
│   ├── gmail.py                # Gmail API wrapper
│   └── google_api.py           # Google Docs/Sheets API wrapper
│
├── templates/
│   └── index.html              # Фронтенд (единый файл)
│
├── credentials.json            # OAuth2 ключи Google (скачать из Cloud Console)
├── token.pickle                # Авторизационный токен (создаётся автоматически)
│
└── README.md                   # Этот файл
```

---

## 🚀 Установка

### 1. Клонирование репозитория
```bash
git clone https://github.com/yourusername/PCAI.git
cd PCAI
```

### 2. Установка зависимостей
```bash
pip install -r requirements.txt
```

**Или вручную:**
```bash
pip install flask lmstudio google-api-python-client google-auth-oauthlib google-auth-httplib2 duckduckgo-search aiohttp beautifulsoup4 lxml
```

### 3. Подготовка `requirements.txt` (если отсутствует)
```txt
flask>=2.3.0
lmstudio>=0.1.0
google-api-python-client>=2.100.0
google-auth>=2.23.0
google-auth-oauthlib>=1.1.0
google-auth-httplib2>=0.1.1
duckduckgo-search>=4.1.0
aiohttp>=3.9.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
```

---

## 🔐 Настройка Google Cloud

### Шаг 1: Создание проекта
1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий

### Шаг 2: Включение API
В разделе **APIs & Services > Library** включите:
- ✅ **Google Docs API**
- ✅ **Google Sheets API**
- ✅ **Gmail API**
- ✅ **Google Drive API** (для прав доступа к файлам)

### Шаг 3: Настройка OAuth
1. Перейдите в **APIs & Services > OAuth consent screen**
2. Выберите **External** → **Create**
3. Заполните обязательные поля:
   - **App name**: `AI Assistant`
   - **User support email**: ваш email
   - **Developer contact**: ваш email
4. В **Scopes** добавьте:
   ```
   https://www.googleapis.com/auth/documents
   https://www.googleapis.com/auth/spreadsheets
   https://www.googleapis.com/auth/gmail.modify
   https://www.googleapis.com/auth/drive.file
   ```
5. В **Test users** добавьте ваш Google-аккаунт (обязательно для режима `Testing`)

### Шаг 4: Создание credentials
1. Перейдите в **APIs & Services > Credentials**
2. **Create Credentials** → **OAuth client ID**
3. Тип приложения: **Desktop app**
4. Скачайте JSON и переименуйте в `credentials.json`
5. Переместите файл в корень проекта (`PCAI/credentials.json`)

> ⚠️ **Важно**: В режиме `Testing` токены автоматически отзываются каждые 7 дней. Для постоянного использования измените статус на **Production** (требуется верификация приложения).

---

## ⚙️ Настройка LM Studio

1. Скачайте и установите [LM Studio](https://lmstudio.ai/)
2. Загрузите любую совместимую модель (рекомендуется):
   - `Qwen/Qwen3-8B-Instruct`
   - `google/gemma-3-12b-it`
   - `meta-llama/Llama-3.1-8B-Instruct`
3. Запустите локальный сервер:
   - Вкладка **Local Server** → **Start Server**
   - Убедитесь, что адрес: `http://localhost:1234`
4. В файле `base.py` проверьте название модели:
   ```python
   model = lms.llm("ваша модель")  # должно совпадать с загруженной
   ```

---

## ▶️ Запуск

### 1. Запустите LM Studio сервер
Убедитесь, что сервер активен на `http://127.0.0.1:1234`

### 2. Запустите Flask приложение
```bash
python app.py
```

### 3. Откройте в браузере
```
http://127.0.0.1:5000
```

### 4. Первая авторизация в Google
При первом использовании Gmail/Docs/Sheets:
1. В терминале появится ссылка `http://localhost:XXXX`
2. Браузер откроет окно авторизации Google
3. Войдите в аккаунт → нажмите **Разрешить**
4. Автоматически создастся файл `token.pickle`

---

## 🎮 Использование

### 💬 Обычный чат
1. Введите сообщение в поле ввода
2. Нажмите `Enter` или кнопку отправки
3. Получите ответ от локальной нейросети

### 🔍 Чат с поиском
1. Нажмите **🔍 Поиск** в панели инструментов
2. Индикатор начнёт пульсировать (поиск активен)
3. Отправьте сообщение → ответ будет обогащён данными из интернета

### 📄 Создание Google Doc
1. Нажмите кнопку **📄 Google Docs**
2. Введите тему документа в модальном окне
3. Нажмите **Создать**
4. В чате появится текст документа + ссылка на ваш Google Диск

### 📊 Создание Google Sheet
1. Нажмите кнопку **📊 Google Sheets**
2. Опишите структуру таблицы (например: *"Таблица сравнения смартфонов: модель, цена, рейтинг"*)
3. Нажмите **Создать**
4. Получите ссылку на заполненную таблицу

### 📧 Работа с Gmail
| Задача | Описание |
|--------|----------|
| 📥 Последние 10 писем | Краткий обзор входящих с темой и отправителем |
| 📖 Прочитать письмо | Выберите номер (1-10) → получите полный текст + анализ от AI |
| ✉️ Написать письмо | Укажите получателя, тему, инструкцию → нейросеть напишет и отправит письмо |

---

## 🌐 API Endpoints

### Чат
| Метод | Эндпоинт | Тело запроса | Ответ |
|-------|----------|--------------|-------|
| `POST` | `/api/chat` | `{"message": "...", "history": "...", "search": false}` | `{"response": "..."}` |

### Документы
| Метод | Эндпоинт | Тело запроса | Ответ |
|-------|----------|--------------|-------|
| `POST` | `/api/document` | `{"prompt": "Тема документа"}` | `{"result": "Текст + ссылка"}` |
| `POST` | `/api/document_no_search` | `{"prompt": "Тема документа"}` | `{"result": "Текст + ссылка"}` |

### Таблицы
| Метод | Эндпоинт | Тело запроса | Ответ |
|-------|----------|--------------|-------|
| `POST` | `/api/table` | `{"prompt": "Описание таблицы"}` | `{"result": "JSON + ссылка"}` |
| `POST` | `/api/table_no_search` | `{"prompt": "Описание таблицы"}` | `{"result": "JSON + ссылка"}` |

### Gmail
| Метод | Эндпоинт | Тело запроса | Ответ |
|-------|----------|--------------|-------|
| `POST` | `/api/gmail` | `{"g_task": "late\|full\|email", "extra": {...}}` | `{"result": "..."}` |

**Пример запроса для отправки письма:**
```json
{
  "g_task": "email",
  "extra": {
    "to": "user@example.com",
    "subject": "Тема письма",
    "instructions": "Напиши деловое предложение о сотрудничестве"
  }
}
```

---

## 🔧 Устранение неполадок


### ❌ `invalid_grant: Token has been expired or revoked`
```bash
# Удалите старый токен и пройдите авторизацию заново
del "token.pickle"
# Затем перезапустите app.py и нажмите любую кнопку Google-интеграции
```


### ❌ Письмо не приходит, но показывается "✅ Успешно"
1. Проверьте папку **Спам** у получателя
2. Убедитесь, что `token.pickle` имеет права `gmail.modify`
3. В Google Cloud Console → OAuth consent screen → **Test users**: добавьте email получателя
4. Проверьте лимиты: бесплатный аккаунт — ~500 писем/день

### ❌ Поиск возвращает "Ничего не найдено"
- Попробуйте переформулировать запрос на английском
- Увеличьте `max_results` в `back/ddg.py`
- Проверьте интернет-соединение и наличие блокировок DuckDuckGo

### ❌ LM Studio не отвечает
- Убедитесь, что сервер запущен на `http://127.0.0.1:1234`
- Проверьте, что модель загружена и статус **Ready**
- В `base.py` название модели должно точно совпадать с загруженной

---


```
Copyright (c) 2025 Vov-dot

Разрешается бесплатное использование, копирование, модификация
и распространение данного ПО при условии сохранения уведомления
о лицензии и авторских правах.
```

---


> ⚠️ **Отказ от ответственности**: Проект использует локальные модели и внешние API. Автор не несёт ответственности за содержание сгенерированных ответов, ошибки нейросетей или проблемы с аккаунтами Google. Используйте на свой страх и риск.

---

Если проект оказался полезным — поставьте ⭐!

