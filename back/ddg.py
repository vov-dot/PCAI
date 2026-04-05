import asyncio
import aiohttp
import random
import re
from bs4 import BeautifulSoup as bs
from ddgs import DDGS

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15'
]

def _clean_page(html: str, url: str, max_chars: int = 1500) -> str | None:
    try:
        soup = bs(html, 'lxml')
        
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'noscript',
                         'meta', 'link', 'img', 'iframe', 'form', 'button', 'input', 'svg', 'comment']):
            tag.decompose()
            
        main = (soup.find('article') or 
                soup.find('main') or 
                soup.find('div', class_=re.compile(r'(post|content|article|entry|main|story)', re.I)) or 
                soup.find('body'))
                
        if not main:
            return None
            
        text = main.get_text(separator='\n', strip=True)
        
        lines = [l.strip() for l in text.split('\n') if len(l.split()) >= 2]
        text = '\n'.join(lines)
        
        if len(text) < 150:
            return None
            
        if len(text) > max_chars:
            text = text[:max_chars].rsplit(' ', 1)[0] + "..."
            
        return f"[Источник: {url}]\n{text}"
    except Exception:
        return None

async def _fetch(session, url: str, timeout: int = 8) -> str | None:
    try:
        headers = {'User-Agent': random.choice(USER_AGENTS), 'Accept-Language': 'ru-RU,ru;q=0.9'}
        async with session.get(url, headers=headers, timeout=timeout, allow_redirects=True) as resp:
            if resp.status == 200:
                return await resp.text(encoding='utf-8', errors='ignore')
    except Exception:
        return None

def search(query: str, max_results: int = 5, max_total_chars: int = 4000) -> str:
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, region="ru-ru", max_results=max_results, safesearch="moderate"))
    except Exception as e:
        return f"❌ Ошибка поиска: {e}"
        
    if not results:
        return "⚠️ Ничего не найдено. Попробуйте переформулировать запрос."
        
    urls = [r.get('href') for r in results if r.get('href')]
    snippets = [f"**{r.get('title', '')}**\n{r.get('body', '')}\n🔗 {r.get('href')}" for r in results]
    
    async def load_all():
        connector = aiohttp.TCPConnector(limit=3)
        timeout = aiohttp.ClientTimeout(total=12)
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            tasks = [_fetch(session, url) for url in urls]
            return await asyncio.gather(*tasks, return_exceptions=True)
            
    pages = asyncio.run(load_all())
    
    contents = []
    total_len = 0
    for url, html in zip(urls, pages):
        if isinstance(html, Exception) or html is None:
            continue
        content = _clean_page(html, url)
        if content:
            contents.append(content)
            total_len += len(content)
            if total_len >= max_total_chars:
                break
                
    if not contents:
        return "📄 **Сниппеты из поиска:**\n\n" + "\n\n".join(snippets[:3])
        
    return "\n\n".join(contents)
