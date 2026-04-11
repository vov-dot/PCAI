# LMStudio Agent

Интеллектуальный ассистент с поддержкой инструментов для работы с LMStudio.

## Возможности

📄 **Работа с документами**
- Создание Word документов (.docx)
- Создание Excel таблиц (.xlsx)
- Редактирование существующих документов
- Чтение данных из Excel файлов

📧 **Электронная почта**
- Отправка email сообщений
- Сохранение черновиков писем

💰 **Сравнение цен**
- Поиск цен на товары в различных магазинах
- Сравнение нескольких товаров
- История изменения цен
- Рекомендации по лучшим сделкам

🛠️ **Утилиты**
- Математические вычисления
- Создание напоминаний
- Работа с файлами
- Информация о системе

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Настройте LMStudio:
   - Скачайте и установите [LMStudio](https://lmstudio.ai/)
   - Загрузите нужную модель
   - Запустите локальный сервер

3. (Опционально) Настройте параметры в `config/settings.json`:
```json
{
    "lmstudio": {
        "base_url": "http://localhost:1234",
        "model_id": null
    },
    "email": {
        "smtp_server": "smtp.example.com",
        "smtp_port": 587,
        "username": "your@email.com",
        "password": "your_password"
    }
}
```

## Использование

### Интерактивный режим
```bash
python main.py --interactive
```

### Одиночный запрос
```bash
# Создать таблицу с ценами
python main.py --query "Создай Excel таблицу с ценами на iPhone и MacBook"

# Сравнить цены
python main.py --query "Сравни цены на iPhone, Samsung Galaxy и Sony headphones"

# Создать документ
python main.py --query "Создай Word документ с отчетом о продажах за квартал"

# Отправить письмо (требуется настройка SMTP)
python main.py --query "Отправь письмо test@example.com с темой 'Привет' и текстом 'Как дела?'"

# Математические вычисления
python main.py --query "Вычисли 2 + 2 * 3.5"
```

### Параметры командной строки
```
--query, -q     Текстовый запрос для обработки
--interactive, -i  Запустить в интерактивном режиме
--url           URL сервера LMStudio (по умолчанию http://localhost:1234)
--model         ID модели для использования
```

## Структура проекта

```
lmstudio-agent/
├── main.py                 # Основной файл запуска
├── requirements.txt        # Зависимости
├── config/
│   └── settings.json      # Конфигурация
├── tools/
│   ├── __init__.py        # Инициализация инструментов
│   ├── tool_registry.py   # Регистрация инструментов
│   ├── document_tools.py  # Работа с документами
│   ├── email_tools.py     # Работа с почтой
│   ├── price_tools.py     # Сравнение цен
│   └── utils_tools.py     # Утилиты
├── output/                # Выходные файлы
│   ├── documents/         # Word документы
│   ├── spreadsheets/      # Excel таблицы
│   ├── email_drafts/      # Черновики писем
│   └── reminders/         # Напоминания
└── docs/                  # Документация
```

## Примеры использования инструментов

### Создание документа
```python
from tools.document_tools import create_word_document

filepath = create_word_document(
    filename="report",
    title="Ежемесячный отчет",
    content="Продажи выросли на 15%..."
)
```

### Создание таблицы
```python
from tools.document_tools import create_excel_table

data = [
    ["iPhone 15", 999, "Apple"],
    ["Samsung S24", 899, "Samsung"],
    ["Pixel 8", 799, "Google"]
]
columns = ["Модель", "Цена", "Производитель"]

filepath = create_excel_table("products", data, columns)
```

### Сравнение цен
```python
from tools.price_tools import search_product_prices, compare_products

# Поиск цен на один товар
prices = search_product_prices("iPhone 15")

# Сравнение нескольких товаров
comparison = compare_products(["iPhone", "Samsung Galaxy", "MacBook"])
```

### Отправка письма
```python
from tools.email_tools import send_email

result = send_email(
    to="recipient@example.com",
    subject="Важное сообщение",
    body="Текст письма...",
    cc="manager@example.com"
)
```

## Добавление новых инструментов

1. Создайте функцию в соответствующем модуле (`tools/`)
2. Добавьте описание в `TOOLS_CONFIG` в `tools/tool_registry.py`
3. Импортируйте функцию в `tools/__init__.py`

Пример:
```python
# В tools/my_tools.py
def my_new_function(param1: str, param2: int) -> dict:
    """Описание функции"""
    return {"result": f"{param1}: {param2}"}

# В tools/tool_registry.py добавьте в TOOLS_CONFIG:
{
    "name": "my_new_function",
    "description": "Описание функции",
    "parameters": [
        {"name": "param1", "type": "string", "description": "Описание параметра"},
        {"name": "param2", "type": "integer", "description": "Описание параметра"}
    ]
}
```

## Требования

- Python 3.8+
- LMStudio с запущенным локальным сервером
- Зависимости из requirements.txt

## Лицензия

MIT
