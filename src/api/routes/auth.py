from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import jwt
import bcrypt
from src.api.schemas import UserCreate, UserLogin
from src.api.dependencies import JWT_SECRET, JWT_ALGORITHM

router = APIRouter()

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

fake_users_db = {
    "testuser": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "password_hash": hash_password("testpass")
    }
}


def create_access_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(hours=24)
    payload = {"sub": user_id, "exp": expire, "iat": datetime.utcnow()}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


@router.post("/register")
async def register(user_data: UserCreate):
    if user_data.username in fake_users_db:
        raise HTTPException(status_code=400, detail="User exists")
    new_id = len(fake_users_db) + 1
    fake_users_db[user_data.username] = {
        "id": new_id,
        "username": user_data.username,
        "email": user_data.email,
        "password_hash": hash_password(user_data.password)
    }
    return {"id": new_id, "username": user_data.username, "email": user_data.email, "message": "User registered"}


@router.post("/login")
async def login(credentials: UserLogin):
    user = fake_users_db.get(credentials.username)
    if not user or not verify_password(credentials.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user['id'])
    return {"access_token": token, "token_type": "bearer", "expires_in": 86400}
