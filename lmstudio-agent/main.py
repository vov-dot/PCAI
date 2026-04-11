"""
LMStudio Agent - Интеллектуальный ассистент с поддержкой инструментов

Этот агент подключается к LMStudio и может:
- Создавать и редактировать документы (Word, Excel)
- Отправлять электронные письма
- Сравнивать цены на товары
- Выполнять различные утилитарные задачи

Использование:
    python main.py --query "Создай таблицу с ценами на iPhone и MacBook"
    python main.py --interactive  # Интерактивный режим
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lmstudio import Client, LMStudioServerError
from tools import get_all_tools, get_function, get_all_function_names


class LMStudioAgent:
    """Агент для работы с LMStudio и инструментами."""
    
    def __init__(self, base_url: str = "http://localhost:1234", model_id: Optional[str] = None):
        """
        Инициализирует агента.
        
        Args:
            base_url: URL сервера LMStudio
            model_id: ID модели (если None, будет использована модель по умолчанию)
        """
        self.base_url = base_url
        self.model_id = model_id
        self.client = None
        self.model = None
        self.conversation_history = []
        
    def connect(self) -> bool:
        """
        Подключается к серверу LMStudio.
        
        Returns:
            True если подключение успешно, иначе False
        """
        try:
            print(f"🔌 Подключение к LMStudio ({self.base_url})...")
            self.client = Client(base_url=self.base_url)
            
            # Получаем список доступных моделей
            models = self.client.list_downloaded_models()
            
            if not models:
                print("❌ Нет загруженных моделей в LMStudio")
                print("💡 Загрузите модель через LMStudio UI")
                return False
            
            # Выбираем модель
            if self.model_id:
                self.model = self.client.get_model(self.model_id)
                print(f"✅ Модель {self.model_id} выбрана")
            else:
                self.model = models[0]
                print(f"✅ Используется модель: {self.model.id}")
            
            return True
            
        except LMStudioServerError as e:
            print(f"❌ Ошибка подключения к LLM: {e}")
            print("💡 Убедитесь, что LMStudio запущен и доступен")
            return False
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            return False
    
    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Выполняет инструмент по имени.
        
        Args:
            tool_name: Имя инструмента
            **kwargs: Аргументы для инструмента
        
        Returns:
            Результат выполнения инструмента
        """
        func = get_function(tool_name)
        
        if not func:
            return {"error": f"Инструмент {tool_name} не найден"}
        
        try:
            print(f"🔧 Выполнение инструмента: {tool_name}")
            result = func(**kwargs)
            print(f"✅ Инструмент выполнен успешно")
            return result
        except Exception as e:
            error_msg = f"Ошибка при выполнении {tool_name}: {str(e)}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}
    
    def process_with_tools(self, query: str, max_iterations: int = 5) -> str:
        """
        Обрабатывает запрос с использованием инструментов.
        
        Args:
            query: Пользовательский запрос
            max_iterations: Максимальное количество итераций
        
        Returns:
            Ответ от агента
        """
        if not self.model:
            return "❌ Агент не подключен к LMStudio"
        
        try:
            # Получаем определения инструментов
            tools = get_all_tools()
            
            # Создаем контекст для разговора
            conversation = self.model.start_chat()
            
            # Добавляем системную инструкцию
            system_prompt = """Ты интеллектуальный помощник с доступом к различным инструментам.
            
Доступные инструменты:
- create_word_document: Создание Word документов
- create_excel_table: Создание Excel таблиц
- send_email/draft_email: Отправка почты
- search_product_prices/compare_products: Сравнение цен
- calculate: Математические вычисления
- create_reminder: Создание напоминаний
- и другие...

Когда пользователь просит выполнить действие, используй соответствующий инструмент.
Всегда предоставляй понятный ответ на русском языке."""

            conversation.add_message("system", system_prompt)
            
            # Добавляем запрос пользователя
            conversation.add_message("user", query)
            
            print(f"\n🤔 Обработка запроса: {query}\n")
            
            # Используем act для обработки с инструментами
            response = ""
            
            for iteration in range(max_iterations):
                # Получаем ответ от модели
                result = conversation.act(
                    tools=tools,
                    on_tool_call=lambda name, args: self.execute_tool(name, **args)
                )
                
                # Проверяем тип результата
                if isinstance(result, str):
                    response = result
                    break
                elif hasattr(result, 'content'):
                    response = result.content
                    break
                else:
                    response = str(result)
                    break
            
            # Сохраняем историю
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "response": response
            })
            
            return response
            
        except Exception as e:
            return f"❌ Ошибка при обработке запроса: {str(e)}"
    
    def chat_interactive(self):
        """Запускает интерактивный режим чата."""
        print("\n" + "="*60)
        print("🤖 LMStudio Agent - Интерактивный режим")
        print("="*60)
        print("Доступные команды:")
        print("  /help     - Показать справку")
        print("  /history  - Показать историю запросов")
        print("  /clear    - Очистить историю")
        print("  /exit     - Выйти из программы")
        print("="*60 + "\n")
        
        while True:
            try:
                query = input("\n👤 Вы: ").strip()
                
                if not query:
                    continue
                
                # Обработка команд
                if query.lower() == '/exit':
                    print("👋 До свидания!")
                    break
                elif query.lower() == '/help':
                    self._show_help()
                    continue
                elif query.lower() == '/history':
                    self._show_history()
                    continue
                elif query.lower() == '/clear':
                    self.conversation_history = []
                    print("🗑️ История очищена")
                    continue
                
                # Обработка запроса
                response = self.process_with_tools(query)
                print(f"\n🤖 Агент: {response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 До свидания!")
                break
            except EOFError:
                print("\n\n👋 До свидания!")
                break
    
    def _show_help(self):
        """Показывает справку по доступным функциям."""
        print("\n📚 Доступные инструменты:")
        for name in sorted(get_all_function_names()):
            print(f"  • {name}")
        print()
    
    def _show_history(self):
        """Показывает историю запросов."""
        if not self.conversation_history:
            print("📭 История пуста")
            return
        
        print(f"\n📜 История запросов ({len(self.conversation_history)}):")
        for i, item in enumerate(self.conversation_history[-5:], 1):
            print(f"\n{i}. [{item['timestamp']}]")
            print(f"   Запрос: {item['query'][:100]}...")
            print(f"   Ответ: {item['response'][:100]}...")
        print()


def load_config() -> Dict:
    """Загружает конфигурацию из файла."""
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'settings.json')
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️ Файл конфигурации не найден: {config_path}")
        return {}
    except json.JSONDecodeError:
        print(f"⚠️ Ошибка чтения файла конфигурации: {config_path}")
        return {}


def main():
    """Основная функция."""
    parser = argparse.ArgumentParser(
        description="LMStudio Agent - Интеллектуальный ассистент с инструментами",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python main.py --query "Создай таблицу с ценами на iPhone"
  python main.py --query "Отправь письмо test@example.com"
  python main.py --interactive
        """
    )
    
    parser.add_argument(
        '--query', '-q',
        type=str,
        help='Текстовый запрос для обработки'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Запустить в интерактивном режиме'
    )
    
    parser.add_argument(
        '--url',
        type=str,
        default=None,
        help='URL сервера LMStudio (по умолчанию из конфига)'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default=None,
        help='ID модели для использования'
    )
    
    args = parser.parse_args()
    
    # Загружаем конфигурацию
    config = load_config()
    
    # Определяем параметры подключения
    base_url = args.url or config.get('lmstudio', {}).get('base_url', 'http://localhost:1234')
    model_id = args.model or config.get('lmstudio', {}).get('model_id')
    
    # Создаем и подключаем агента
    agent = LMStudioAgent(base_url=base_url, model_id=model_id)
    
    if not agent.connect():
        print("\n💡 Для запуска агента:")
        print("   1. Установите LMStudio: https://lmstudio.ai/")
        print("   2. Загрузите модель")
        print("   3. Запустите локальный сервер")
        sys.exit(1)
    
    # Создаем директорию для выходных файлов
    os.makedirs('output', exist_ok=True)
    
    # Обрабатываем запросы
    if args.query:
        response = agent.process_with_tools(args.query)
        print(f"\n🤖 Ответ: {response}")
    elif args.interactive:
        agent.chat_interactive()
    else:
        print("\n💡 Используйте --query для отправки запроса или --interactive для интерактивного режима")
        print("   Пример: python main.py --query 'Сравни цены на iPhone и Samsung'")
        print("   Или: python main.py --interactive")


if __name__ == "__main__":
    main()
