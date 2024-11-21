from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.database import Base

class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True)
    product_id = Column(String, index=True)
    product_name = Column(String)
    category = Column(String, index=True)
    quantity = Column(Integer)
    unit_price = Column(Float)
    total_value = Column(Float)
    supplier = Column(String, index=True)
    transaction_type = Column(String)
    transaction_date = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Analytical fields
    year = Column(Integer)
    month = Column(Integer)
    day_of_week = Column(Integer)
    avg_price_per_category = Column(Float)
    transactions_per_product = Column(Integer)

    # Create indexes for commonly queried fields
    __table_args__ = (
        Index('idx_transaction_date_category', transaction_date, category),
        Index('idx_product_transaction_type', product_id, transaction_type),
    )

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String, unique=True, index=True)
    name = Column(String)
    category = Column(String, index=True)
    description = Column(String, nullable=True)
    unit_price = Column(Float)
    stock_level = Column(Integer, default=0)
    reorder_point = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class AnalyticsSnapshot(Base):
    __tablename__ = "analytics_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    snapshot_date = Column(DateTime(timezone=True), server_default=func.now())
    category = Column(String, index=True)
    total_transactions = Column(Integer)
    total_value = Column(Float)
    avg_transaction_value = Column(Float)
    stock_turnover_rate = Column(Float)

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(String, unique=True, index=True)
    name = Column(String)
    contact_person = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())