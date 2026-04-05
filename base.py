import lmstudio as lms
from back import ddg, gmail
from back.google_api import create_google_doc, create_google_sheet

model = lms.llm("google/gemma-3-4b")


def create_search_response(prompt: str) -> str:
    """Генерирует короткий поисковый запрос."""
    res = model.respond(
        f'Создай максимально точный запрос для поисковика по теме: "{prompt}". Только сам запрос, без лишних слов. Максимум 30 слов.',
        config={"temperature": 0.4, "maxTokens": 100}
    )
    return str(res).strip()


def document(prompt: str) -> str:
    search_q = create_search_response(prompt)
    search_res = ddg.search(search_q)
    content = model.respond(
        f'Напиши полноценный документ по теме: "{prompt}"\n\nРезультаты поиска для контекста:\n{search_res}\n\nОформи текст структурированно, с заголовками и списками.',
        config={"temperature": 0.6, "maxTokens": 8000}
    )
    link = create_google_doc(str(content), f"Doc_{hash(prompt)}_with_search")
    return f"{content}\n\n🔗 [Открыть Google Doc]({link})"


def document_no_search(prompt: str) -> str:
    content = model.respond(
        f'Напиши полноценный документ по теме: "{prompt}". Оформи структурированно.',
        config={"temperature": 0.6, "maxTokens": 8000}
    )
    link = create_google_doc(str(content), f"Doc_{hash(prompt)}_no_search")
    return f"{content}\n\n🔗 [Открыть Google Doc]({link})"


def table(prompt: str) -> str:
    search_q = create_search_response(prompt)
    search_res = ddg.search(search_q)
    content = model.respond(
        f'''СОЗДАЙ СТРУКТУРИРОВАННУЮ ТАБЛИЦУ.
        Задача: {prompt}
        Контекст из поиска: {search_res}

        ВЫВОДИ ТОЛЬКО ДАННЫЕ В ФОРМАТЕ JSON массива объектов. БЕЗ markdown, БЕЗ пояснений.
        Пример:
        [{{"Название":"X","Цена":"Y"}}, {{"Название":"Z","Цена":"W"}}]''',
        config={"temperature": 0.3, "maxTokens": 5000}
    )
    link = create_google_sheet(str(content), f"Sheet_{hash(prompt)}_with_search")
    return f"{content}\n\n🔗 [Открыть Google Sheet]({link})"


def table_no_search(prompt: str) -> str:
    content = model.respond(
        f'''СОЗДАЙ СТРУКТУРИРОВАННУЮ ТАБЛИЦУ.
        Задача: {prompt}

        ВЫВОДИ ТОЛЬКО ДАННЫЕ В ФОРМАТЕ JSON массива объектов. БЕЗ markdown, БЕЗ пояснений.''',
        config={"temperature": 0.3, "maxTokens": 5000}
    )
    link = create_google_sheet(str(content), f"Sheet_{hash(prompt)}_no_search")
    return f"{content}\n\n🔗 [Открыть Google Sheet]({link})"

def chat(message: str, history_str: str = "") -> str:
    full_prompt = f"История диалога:\n{history_str}\n\nПользователь: {message}\nAI:"
    res = model.respond(full_prompt, config={"temperature": 0.7, "maxTokens": 2000})
    return str(res)

def chat_search(message: str, history_str: str = "") -> str:
    search_q = create_search_response(message)
    search_res = ddg.search(search_q)
    full_prompt = f"История диалога:\n{history_str}\n\nПользователь: {message}\nконтекст из интренета:{search_res}\nAI:"
    res = model.respond(full_prompt, config={"temperature": 0.7, "maxTokens": 2000})
    return str(res)

def gmail_action(g_task, extra=None):
    if extra is None: extra = {}
    
    if g_task == 'late':
        mail_text = gmail.start(task='late')
        result = model.respond(
            f'Очень кратко опиши все письма\nпочта: {mail_text}\nотвечай на русском',
            config={"temperature": 0.6, "maxTokens": 10000}
        )
        return str(result)
        
    elif g_task == 'full':
        num = int(extra.get("num", 1))
        mail_text = gmail.start(task='full', num=num)
        result = model.respond(
            f'Подробно опиши о чем говорится в письме\nпочта: {mail_text}\nотвечай на русском',
            config={"temperature": 0.6, "maxTokens": 10000}
        )
        return str(result)
        
    elif g_task == 'email':
        to = extra.get("to")
        subject = extra.get("subject")
        instructions = extra.get("instructions", "")
        
        body = model.respond(
            f'напиши письмо для gmail\nтема: {subject}\nинструкции: {instructions}\nотвечай на русском',
            config={"temperature": 0.6, "maxTokens": 10000}
        )
        # Реальная отправка через ваш gmail.py
        gmail.start(task='email', to=to, subject=subject, body=str(body))
        return f"✅ Письмо успешно отправлено на {to}.\nТема: {subject}\nСодержание:\n{body}"
        
    else:
        return "Unknown g_task"
