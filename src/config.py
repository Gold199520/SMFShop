from dotenv import load_dotenv
import os

load_dotenv()

# База данных
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/sfmshop")

# Секретные ключи
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
JWT_SECRET = os.getenv("JWT_SECRET", "default-jwt-secret")

# Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Режим отладки
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
