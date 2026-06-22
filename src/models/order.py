class Order:
    def __init__(self, id, user_id, total, status):
        self.id = id
        self.user_id = user_id
        self.total = total
        self.status = status
        self.items = []
    
    def add_item(self, product, quantity=1):
        self.items.append({"product": product, "quantity": quantity})
    
    def calculate_total(self):
        return sum(item["product"].price * item["quantity"] for item in self.items)
    
    def update_status(self, new_status):
        valid_statuses = ["pending", "paid", "shipped", "delivered", "cancelled"]
        if new_status not in valid_statuses:
            raise ValueError("Неверный статус заказа")
        self.status = new_status
    
    def get_summary(self):
        return {
            "order_id": self.id,
            "total_items": len(self.items),
            "items": self.items,
            "total_price": self.calculate_total()
        }
