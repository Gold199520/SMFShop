import requests

def calculate_discount(order_total):
    """Рассчет скидки на основе суммы заказа"""
    if order_total < 0:
        raise ValueError("Сумма заказа не может быть отрицательной")
    
    if order_total >= 10000:
        return order_total * 0.8  # 20% скидка
    elif order_total >= 5000:
        return order_total * 0.9  # 10% скидка
    elif order_total >= 1000:
        return order_total * 0.95  # 5% скидка
    else:
        return order_total  # без скидки


def calculate_delivery(order_total):
    """Рассчет стоимости доставки"""
    if order_total < 0:
        raise ValueError("Сумма заказа не может быть отрицательной")
    
    if order_total < 1000:
        return 500  # платная доставка
    else:
        return 0  # бесплатная доставка


def get_product_reviews(product_id):
    """Получает отзывы о товаре из внешнего API"""
    response = requests.get(f"https://api.example.com/products/{product_id}/reviews")
    if response.status_code == 200:
        return response.json()
    return []