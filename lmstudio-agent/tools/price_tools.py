"""
Модуль для сравнения цен на товары
Симулирует поиск цен по различным источникам
"""
import random
from datetime import datetime
from typing import List, Dict


# Симулированная база данных цен
PRODUCT_DATABASE = {
    "iphone": [
        {"store": "Apple Store", "price": 999, "currency": "USD", "availability": "В наличии"},
        {"store": "Amazon", "price": 949, "currency": "USD", "availability": "В наличии"},
        {"store": "Best Buy", "price": 979, "currency": "USD", "availability": "Ограничено"},
        {"store": "eBay", "price": 899, "currency": "USD", "availability": "Б/У available"},
    ],
    "macbook": [
        {"store": "Apple Store", "price": 1299, "currency": "USD", "availability": "В наличии"},
        {"store": "Amazon", "price": 1249, "currency": "USD", "availability": "В наличии"},
        {"store": "Best Buy", "price": 1279, "currency": "USD", "availability": "В наличии"},
        {"store": "B&H Photo", "price": 1299, "currency": "USD", "availability": "В наличии"},
    ],
    "samsung galaxy": [
        {"store": "Samsung Store", "price": 899, "currency": "USD", "availability": "В наличии"},
        {"store": "Amazon", "price": 849, "currency": "USD", "availability": "В наличии"},
        {"store": "Best Buy", "price": 879, "currency": "USD", "availability": "В наличии"},
        {"store": "Walmart", "price": 869, "currency": "USD", "availability": "Ограничено"},
    ],
    "sony headphones": [
        {"store": "Sony Store", "price": 349, "currency": "USD", "availability": "В наличии"},
        {"store": "Amazon", "price": 329, "currency": "USD", "availability": "В наличии"},
        {"store": "Best Buy", "price": 349, "currency": "USD", "availability": "В наличии"},
        {"store": "Target", "price": 339, "currency": "USD", "availability": "В наличии"},
    ],
}


def search_product_prices(product_name: str) -> Dict:
    """
    Ищет цены на товар в различных магазинах.
    
    Args:
        product_name: Название товара для поиска
    
    Returns:
        Словарь с найденными ценами и информацией
    """
    product_name_lower = product_name.lower()
    
    # Ищем совпадения в базе данных
    results = []
    for key, prices in PRODUCT_DATABASE.items():
        if key in product_name_lower or product_name_lower in key:
            results.extend(prices)
    
    # Если ничего не найдено, генерируем симулированные данные
    if not results:
        stores = ["Amazon", "eBay", "Walmart", "Target", "Best Buy", "AliExpress"]
        base_price = random.randint(50, 2000)
        
        for store in random.sample(stores, random.randint(3, 5)):
            price_variation = random.uniform(0.8, 1.2)
            results.append({
                "store": store,
                "price": round(base_price * price_variation, 2),
                "currency": "USD",
                "availability": random.choice(["В наличии", "Ограничено", "Под заказ"]),
                "shipping": random.choice(["Бесплатно", "$5.99", "$9.99", "2 дня"])
            })
    
    # Сортируем по цене
    results.sort(key=lambda x: x["price"])
    
    # Находим лучшую цену
    best_price = results[0] if results else None
    avg_price = sum(item["price"] for item in results) / len(results) if results else 0
    
    return {
        "product": product_name,
        "search_timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "results_count": len(results),
        "best_offer": best_price,
        "average_price": round(avg_price, 2),
        "all_offers": results,
        "price_range": {
            "min": results[0]["price"] if results else 0,
            "max": results[-1]["price"] if results else 0
        }
    }


def compare_products(products: List[str]) -> Dict:
    """
    Сравнивает цены на несколько товаров.
    
    Args:
        products: Список названий товаров для сравнения
    
    Returns:
        Сравнительная таблица цен
    """
    comparison = {}
    
    for product in products:
        price_data = search_product_prices(product)
        comparison[product] = {
            "best_price": price_data["best_offer"],
            "average_price": price_data["average_price"],
            "stores_count": price_data["results_count"]
        }
    
    # Находим самый выгодный товар относительно средней цены
    total_value = sum(item["average_price"] for item in comparison.values())
    
    return {
        "comparison_timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "products_compared": len(products),
        "comparison_data": comparison,
        "total_estimated_value": round(total_value, 2),
        "recommendation": get_best_deal_recommendation(comparison)
    }


def get_best_deal_recommendation(comparison: Dict) -> str:
    """
    Генерирует рекомендацию по лучшей покупке.
    """
    if not comparison:
        return "Нет данных для рекомендации"
    
    best_deal = None
    best_savings = 0
    
    for product, data in comparison.items():
        if data["best_price"]:
            savings = data["average_price"] - data["best_price"]["price"]
            if savings > best_savings:
                best_savings = savings
                best_deal = {
                    "product": product,
                    "store": data["best_price"]["store"],
                    "savings": round(savings, 2)
                }
    
    if best_deal:
        return f"Лучшая сделка: {best_deal['product']} в {best_deal['store']} (экономия ${best_deal['savings']})"
    else:
        return "Рекомендаций нет"


def get_price_history(product_name: str) -> Dict:
    """
    Симулирует историю изменения цен на товар.
    
    Args:
        product_name: Название товара
    
    Returns:
        История цен за последние 30 дней
    """
    current_data = search_product_prices(product_name)
    base_price = current_data["average_price"]
    
    history = []
    for days_ago in range(30, 0, -1):
        # Симулируем колебания цен
        variation = random.uniform(-0.15, 0.1)
        price = round(base_price * (1 + variation), 2)
        
        history.append({
            "date": f"{days_ago} дней назад",
            "avg_price": price,
            "min_price": round(price * 0.9, 2),
            "max_price": round(price * 1.1, 2)
        })
    
    return {
        "product": product_name,
        "current_price": base_price,
        "history": history,
        "trend": "снижение" if history[-1]["avg_price"] < history[0]["avg_price"] else "рост",
        "price_change": round(history[-1]["avg_price"] - history[0]["avg_price"], 2)
    }
