import pytest
from src.models.product import Product
from src.models.user import User
from src.models.order import Order


@pytest.fixture
def sample_product():
    """Фикстура: тестовый товар"""
    return Product(id=1, name="Тестовый товар", price=1000, quantity=10)


@pytest.fixture
def sample_user():
    """Фикстура: тестовый пользователь"""
    return User(id=1, name="Тестовый пользователь", email="test@example.ru")


@pytest.fixture
def sample_order(sample_user):
    """Фикстура: тестовый заказ"""
    return Order(id=1, user_id=sample_user.id, total=0, status="pending")


# Тесты для Product
def test_create_product(sample_product):
    """Тест: создание товара"""
    assert sample_product.id == 1
    assert sample_product.name == "Тестовый товар"
    assert sample_product.price == 1000


def test_product_validation(sample_product):
    """Тест: валидация товара"""
    assert sample_product.price > 0
    assert sample_product.quantity >= 0


def test_product_update_price(sample_product):
    """Тест: обновление цены"""
    sample_product.update_price(1500)
    assert sample_product.price == 1500


def test_product_update_quantity(sample_product):
    """Тест: обновление количества"""
    sample_product.update_quantity(5)
    assert sample_product.quantity == 5


# Тесты для User
def test_create_user(sample_user):
    """Тест: создание пользователя"""
    assert sample_user.id == 1
    assert sample_user.email == "test@example.ru"


def test_user_email_validation(sample_user):
    """Тест: валидация email"""
    assert "@" in sample_user.email


# Тесты для Order
def test_create_order(sample_order):
    """Тест: создание заказа"""
    assert sample_order.id == 1
    assert sample_order.status == "pending"


def test_order_calculate_total(sample_order, sample_product):
    """Тест: расчет стоимости заказа"""
    sample_order.add_item(sample_product, quantity=2)
    total = sample_order.calculate_total()
    assert total == sample_product.price * 2  # 1000 * 2 = 2000

# Дополнительные тесты для достижения >80% покрытия

def test_product_reduce_quantity(sample_product):
    """Тест: уменьшение количества товара"""
    sample_product.reduce_quantity(3)
    assert sample_product.quantity == 7


def test_product_reduce_quantity_insufficient(sample_product):
    """Тест: ошибка при недостатке товара"""
    with pytest.raises(ValueError, match="Недостаточно товара на складе"):
        sample_product.reduce_quantity(99)


def test_user_deactivate(sample_user):
    """Тест: деактивация пользователя"""
    sample_user.deactivate()
    assert sample_user.is_active is False


def test_order_update_status(sample_order):
    """Тест: обновление статуса заказа"""
    sample_order.update_status("paid")
    assert sample_order.status == "paid"


def test_order_update_status_invalid(sample_order):
    """Тест: неверный статус"""
    with pytest.raises(ValueError):
        sample_order.update_status("invalid")


def test_calculate_discount_negative():
    """Тест: отрицательная сумма скидки"""
    with pytest.raises(ValueError):
        from src.utils.calculations import calculate_discount
        calculate_discount(-100)


def test_calculate_delivery_negative():
    """Тест: отрицательная сумма доставки"""
    with pytest.raises(ValueError):
        from src.utils.calculations import calculate_delivery
        calculate_delivery(-100)
