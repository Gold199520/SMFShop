from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    category: str = Field(..., min_length=1)

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Название не может быть пустым')
        return v.strip()

    @validator('price')
    def validate_price(cls, v):
        if v > 1000000:
            raise ValueError('Цена не может превышать 1,000,000')
        return round(v, 2)

    @validator('stock')
    def validate_stock(cls, v):
        if v > 10000:
            raise ValueError('Количество на складе не может превышать 10,000')
        return v


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    category: Optional[str] = Field(None, min_length=1)


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)

    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Пароль должен содержать хотя бы одну заглавную букву')
        if not any(c.isdigit() for c in v):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class OrderCreate(BaseModel):
    items: List[dict] = Field(..., min_items=1)

    @validator('items')
    def validate_items(cls, v):
        for item in v:
            if 'product_id' not in item or 'quantity' not in item:
                raise ValueError('Каждый товар должен содержать product_id и quantity')
            if item['quantity'] < 1:
                raise ValueError('Количество товара должно быть больше 0')
        return v


class OrderResponse(BaseModel):
    id: int
    user_id: int
    items: List[dict]
    total_amount: float
    status: str
    created_at: datetime