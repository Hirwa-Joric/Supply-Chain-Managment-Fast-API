from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# IMS Schemas
class SupplierBase(BaseModel):
    name: str
    contact_person: str
    email: EmailStr
    phone: str
    address: Optional[str] = None

class SupplierCreate(SupplierBase):
    pass

class Supplier(SupplierBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    name: str
    sku: str
    description: Optional[str] = None
    unit_price: float
    stock_quantity: int
    reorder_point: int
    category: str
    supplier_id: int

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# OMS Schemas
class CustomerBase(BaseModel):
    name: str
    email: EmailStr
    phone: str
    address: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class OrderItemBase(BaseModel):
    product_sku: str
    quantity: int
    unit_price: float
    total_price: float

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    order_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    customer_id: int
    status: str
    shipping_address: str
    total_amount: float = 0

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class Order(OrderBase):
    id: int
    order_date: datetime
    created_at: datetime
    items: List[OrderItem]

    class Config:
        from_attributes = True

# Analytics Schemas
class InventoryAnalytics(BaseModel):
    total_products: int
    total_value: float
    low_stock_items: int
    categories_distribution: dict
    avg_price_by_category: dict

class OrderAnalytics(BaseModel):
    total_orders: int
    total_revenue: float
    avg_order_value: float
    orders_by_status: dict
    top_selling_products: List[dict]
