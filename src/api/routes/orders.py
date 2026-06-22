from fastapi import APIRouter

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.get("/")
async def get_orders():
    return [{"id": 1, "user_id": 1, "status": "pending", "total": 0}]

@router.post("/")
async def create_order(user_id: int):
    return {"order_id": 1, "status": "accepted"}

@router.get("/{order_id}")
async def get_order(order_id: int):
    return {"id": order_id, "user_id": 1, "status": "pending", "total": 0}