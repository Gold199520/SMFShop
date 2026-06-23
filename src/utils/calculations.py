import httpx

def calculate_discount(order_total):
    """Рассчет скидки на основе суммы заказа"""
    if order_total < 0:
        raise ValueError("Сумма заказа не может быть отрицательной")
    if order_total >= 10000:
        return order_total * 0.8
    elif order_total >= 5000:
        return order_total * 0.9
    elif order_total >= 1000:
        return order_total * 0.95
    else:
        return order_total


def calculate_delivery(order_total):
    """Рассчет стоимости доставки"""
    if order_total < 0:
        raise ValueError("Сумма заказа не может быть отрицательной")
    if order_total < 1000:
        return 500
    else:
        return 0


def get_product_reviews(product_id):
    """Получает отзывы о товаре из внешнего API"""
    try:
        response = httpx.get(f"https://api.example.com/products/{product_id}/reviews")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []
