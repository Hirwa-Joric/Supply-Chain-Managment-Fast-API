from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    quantity: int
    category: str

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class SupplierBase(BaseModel):
    name: str
    contact: str
    email: str
    address: str

class SupplierCreate(SupplierBase):
    pass

class Supplier(SupplierBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class OrderBase(BaseModel):
    product_id: int
    quantity: int
    total_price: float
    status: str

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
