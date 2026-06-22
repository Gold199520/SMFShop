class Product:
    def __init__(self, id, name, price, quantity):
        self.id = id
        self.name = name
        self.price = price
        self.quantity = quantity

    def update_price(self, new_price):
        self.price = new_price

    def update_quantity(self, new_quantity):
        self.quantity = new_quantity

    def reduce_quantity(self, amount):
        if amount > self.quantity:
            raise ValueError("Недостаточно товара на складе")
        self.quantity -= amount
