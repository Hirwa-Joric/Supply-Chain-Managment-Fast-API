from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base

# Inventory Management System (IMS) Models
class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    contact_person = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    address = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    products = relationship("Product", back_populates="supplier")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    sku = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)
    unit_price = Column(Float)
    stock_quantity = Column(Integer)
    reorder_point = Column(Integer)
    category = Column(String)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    supplier = relationship("Supplier", back_populates="products")

# Order Management System (OMS) Models
class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    address = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    orders = relationship("Order", back_populates="customer")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    status = Column(String)  # pending, processing, shipped, delivered, cancelled
    order_date = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float, default=0)
    shipping_address = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_sku = Column(String, index=True)  # Reference to IMS product
    quantity = Column(Integer)
    unit_price = Column(Float)
    total_price = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    order = relationship("Order", back_populates="items")
