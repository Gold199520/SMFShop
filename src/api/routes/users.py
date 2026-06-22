from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/")
async def get_users():
    return [{"id": 1, "name": "Тестовый пользователь", "email": "test@example.ru"}]

@router.get("/{user_id}")
async def get_user(user_id: int):
    return {"id": user_id, "name": "Тестовый пользователь", "email": "test@example.ru"}