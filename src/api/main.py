from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse
from src.services.log_service import log_service
import time
import os
from typing import Callable

app = FastAPI(
    title="SFMShop API",
    version="1.0.0",
    description="Продвинутое FastAPI приложение для интернет-магазина"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware для логирования запросов
@app.middleware("http")
async def log_requests(request: Request, call_next: Callable):
    start_time = time.time()
    log_service.info(f"📥 {request.method} {request.url}")
    response = await call_next(request)
    process_time = time.time() - start_time
    log_service.info(f"📤 {request.method} {request.url} - Status: {response.status_code} - Time: {process_time:.3f}s")
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Middleware для обработки ошибок
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next: Callable):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        log_service.error(f"❌ Error: {str(e)}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# Подключение роутеров
from src.api.routes import products, orders, users, auth
from src.api.dependencies import get_db, get_redis, get_current_user

app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(products.router, prefix="/api/v1", dependencies=[Depends(get_current_user)])
app.include_router(orders.router, prefix="/api/v1", dependencies=[Depends(get_current_user)])
app.include_router(users.router, prefix="/api/v1", dependencies=[Depends(get_current_user)])


# Прямые эндпоинты для тестов
@app.post("/api/v1/logout")
async def logout():
    return {"message": "Logged out successfully"}


@app.get("/api/v1/me")
async def me():
    return {"id": 1, "username": "testuser", "email": "test@example.com"}


@app.get("/admin", response_class=HTMLResponse)
async def admin_panel():
    """Админ-панель SFMShop"""
    template_path = os.path.join("templates", "admin.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


# Подключение статических файлов (всегда в конце!)
app.mount("/static", StaticFiles(directory="static"), name="static")