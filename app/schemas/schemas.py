from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, List, Dict

# Transaction Schemas
class TransactionBase(BaseModel):
    product_id: str
    product_name: str
    category: str
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)
    supplier: str
    transaction_type: str
    is_active: bool = True

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    is_active: Optional[bool] = None

class Transaction(TransactionBase):
    id: int
    transaction_id: str
    total_value: float
    transaction_date: datetime
    year: int
    month: int
    day_of_week: int
    avg_price_per_category: float
    transactions_per_product: int

    class Config:
        from_attributes = True

# Product Schemas
class ProductBase(BaseModel):
    product_id: str
    name: str
    category: str
    description: Optional[str] = None
    unit_price: float
    reorder_point: int = 0

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    unit_price: Optional[float] = None
    reorder_point: Optional[int] = None

class Product(ProductBase):
    id: int
    stock_level: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# Supplier Schemas
class SupplierBase(BaseModel):
    supplier_id: str
    name: str
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None

class Supplier(SupplierBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# Analytics Schemas
class AnalyticsBase(BaseModel):
    category: str
    total_transactions: int
    total_value: float
    avg_transaction_value: float
    stock_turnover_rate: float

class AnalyticsSnapshot(AnalyticsBase):
    id: int
    snapshot_date: datetime

    class Config:
        from_attributes = True

class AnalyticsSummary(BaseModel):
    total_transactions: int
    total_value: float
    avg_transaction_value: float
    category_distribution: Dict[str, int]
    transaction_type_distribution: Dict[str, int]
    monthly_trends: List[Dict[str, any]]

    class Config:
        arbitrary_types_allowed = True

# Query Schemas
class DateRangeParams(BaseModel):
    start_date: datetime
    end_date: datetime = Field(default_factory=datetime.utcnow)
    category: Optional[str] = None

class PaginationParams(BaseModel):
    skip: int = 0
    limit: int = 100