class User:
    def __init__(self, id, name, email, is_active=True):
        self.id = id
        self.name = name
        self.email = email
        self.is_active = is_active
    
    def deactivate(self):
        self.is_active = False
    
    def activate(self):
        self.is_active = True
