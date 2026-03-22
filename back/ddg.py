import asyncio
import aiohttp
import random
from bs4 import BeautifulSoup as bs
from ddgs import DDGS



USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
]



def clean_page_content(html, max_length=300000): 
    try:
        soup = bs(html, 'lxml')
        
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'noscript', 
                        'meta', 'link', 'img', 'iframe', 'form', 'button', 'input']):
            tag.decompose()
        
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
        
        if main_content:
            text = main_content.get_text(separator=' ', strip=True)
        else:
            text = soup.get_text(separator=' ', strip=True)
        
        clean_text = ' '.join(text.split())
        
        if len(clean_text) > max_length:
            clean_text = clean_text[:max_length] + "..."
            print(f"Текст обрезан с {len(clean_text)} до {max_length} символов")
        
        return clean_text
    except Exception as e:
        return f"[Ошибка очистки: {e}]"



async def fetch_page(session, url, timeout=10):
    try:
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        async with session.get(url, headers=headers, timeout=timeout) as response:
            if response.status == 200:
                return await response.text()
    except Exception as e:
        return f"[Ошибка: {e}]"



def search(query, max_results=5):
    try:
        search_results = DDGS().text(query, region="ru-ru", max_results=max_results)
        urls = [r['href'] for r in search_results if 'href' in r]
    except Exception as e:
        return f"Ошибка поиска: {e}"
    
    if not urls:
        return "Ничего не найдено"
    
    print(f" Найдено ссылок: {len(urls)}")
    
    async def load_all():
        connector = aiohttp.TCPConnector(limit=5)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = [fetch_page(session, url) for url in urls]
            return await asyncio.gather(*tasks)
    
    html_pages = asyncio.run(load_all())
    
    result_parts = []
    for i, (url, html) in enumerate(zip(urls, html_pages), 1):
        content = clean_page_content(html)
        result_parts.append(f"\n--- ИСТОЧНИК {i}: {url} ---\n{content}\n")
    
    final_text = '\n'.join(result_parts)
    if len(final_text) >= 150000:
        final_text = final_text[:150000]
    print(f"Загружено: {len(final_text)} символов")
    
    return final_text

