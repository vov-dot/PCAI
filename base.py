import lmstudio as lms
from back import word, exel, gmail, ddg

model = lms.llm("google/gemma-3-4b")

def create_search_response(prompt):
    result = model.respond(
        f'создай запрос для поисковика для информации на тему {prompt} (не более 30 слов) КРОМЕ САМОГО ЗАПРОСА ТЕКСТА НЕ ДОЛЖНО БЫТЬ',
        config={"temperature": 0.6, "maxTokens": 150},
    )
    print (str(result))
    return str(result)


def document(request_ai):
    request_search = create_search_response(request_ai)
    search_res = ddg.search(request_search)
    result = model.respond(
        f'напиши файл под word по теме {request_ai}\n результаты поиска в интернете: {search_res}',
        config={"temperature": 0.6, "maxTokens": 10000},
    )
    word.create_doc(text=str(result))
    return str(result)

def table(request_ai):
    request_search = request_ai #подумать на что поменять
    search_res = ddg.search(request_search)
    result = model.respond(
        f'''Извлеки данные из текста и представь их в виде простого текстового списка, где значения разделены точкой с запятой (;).
        Правила:
        Не используй рамки таблицы | или тире.
        Каждая строка данных — это новая строка.
        Первая строка — это заголовки.
        Разделитель — только ;.
        {request_ai}\n результаты поиска в интернете: {search_res}''',
        config={"temperature": 0.6, "maxTokens": 10000},
    )
    exel.text_to_excel(text=str(result))
    return str(result)

def gmail_action( g_task, extra=None):
    if extra is None:
        extra = {}
    if g_task == 'late':
        mail_text = gmail.start(task=g_task)
        result = model.respond(
            f'Очень кратко опиши все письма\n почта: {mail_text} отвечай на русском',
            config={"temperature": 0.6, "maxTokens": 10000},
        )
        return str(result)
    elif g_task == 'full':
        num = int(extra.get("num", 1))
        mail_text = gmail.start(task=g_task, num=num)
        result = model.respond(
            f'Подробно опиши о чем говорится в письме\n почта: {mail_text} отвечай на русском',
            config={"temperature": 0.6, "maxTokens": 10000},
        )
        return str(result)
    elif g_task == 'email':
        to = extra.get("to")
        subject = extra.get("subject")
        instructions = extra.get("instructions", "")
        result = model.respond(
            f'напиши письмо для gmail\n тема-{subject} инструкции {instructions} отвечай на русском',
            config={"temperature": 0.6, "maxTokens": 10000},
        )
        gmail.start(task=g_task, to=to, subject=subject, body=str(result))
        return str(result)
    else:
        return "Unknown g_task"
