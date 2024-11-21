import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
import json
from datetime import datetime, timedelta

# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)

def test_create_transaction(client):
    transaction_data = {
        "product_id": "PRD001",
        "product_name": "Test Product",
        "category": "Electronics",
        "quantity": 10,
        "unit_price": 100.0,
        "supplier": "Test Supplier",
        "transaction_type": "PURCHASE",
        "is_active": True
    }
    
    response = client.post(
        "/api/v1/inventory/transactions/",
        json=transaction_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == transaction_data["product_id"]
    assert data["quantity"] == transaction_data["quantity"]

def test_list_transactions(client):
    # First create a transaction
    transaction_data = {
        "product_id": "PRD001",
        "product_name": "Test Product",
        "category": "Electronics",
        "quantity": 10,
        "unit_price": 100.0,
        "supplier": "Test Supplier",
        "transaction_type": "PURCHASE",
        "is_active": True
    }
    client.post("/api/v1/inventory/transactions/", json=transaction_data)
    
    response = client.get("/api/v1/inventory/transactions/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert isinstance(data, list)

def test_get_analytics_summary(client):
    # Create some test data first
    transaction_data = {
        "product_id": "PRD001",
        "product_name": "Test Product",
        "category": "Electronics",
        "quantity": 10,
        "unit_price": 100.0,
        "supplier": "Test Supplier",
        "transaction_type": "PURCHASE",
        "is_active": True
    }
    client.post("/api/v1/inventory/transactions/", json=transaction_data)
    
    response = client.get("/api/v1/analytics/summary/")
    assert response.status_code == 200
    data = response.json()
    assert "total_transactions" in data
    assert "total_value" in data
    assert "category_distribution" in data

def test_create_product(client):
    product_data = {
        "product_id": "PRD001",
        "name": "Test Product",
        "category": "Electronics",
        "unit_price": 100.0,
        "reorder_point": 10
    }
    
    response = client.post(
        "/api/v1/inventory/products/",
        json=product_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == product_data["product_id"]
    assert data["name"] == product_data["name"]

def test_list_products(client):
    # First create a product
    product_data = {
        "product_id": "PRD001",
        "name": "Test Product",
        "category": "Electronics",
        "unit_price": 100.0,
        "reorder_point": 10
    }
    client.post("/api/v1/inventory/products/", json=product_data)
    
    response = client.get("/api/v1/inventory/products/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert isinstance(data, list)

def test_get_stock_alerts(client):
    # Create a product with low stock
    product_data = {
        "product_id": "PRD001",
        "name": "Test Product",
        "category": "Electronics",
        "unit_price": 100.0,
        "reorder_point": 20,
        "stock_level": 10
    }
    client.post("/api/v1/inventory/products/", json=product_data)
    
    response = client.get("/api/v1/inventory/stock-alerts/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert isinstance(data, list)

def test_update_product(client):
    # First create a product
    product_data = {
        "product_id": "PRD001",
        "name": "Test Product",
        "category": "Electronics",
        "unit_price": 100.0,
        "reorder_point": 10
    }
    client.post("/api/v1/inventory/products/", json=product_data)
    
    # Update the product
    update_data = {
        "name": "Updated Product",
        "unit_price": 150.0
    }
    response = client.put(
        f"/api/v1/inventory/products/PRD001",
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["unit_price"] == update_data["unit_price"]

def test_category_analysis(client):
    # Create some test transactions
    for i in range(3):
        transaction_data = {
            "product_id": f"PRD00{i}",
            "product_name": f"Test Product {i}",
            "category": "Electronics",
            "quantity": 10,
            "unit_price": 100.0,
            "supplier": "Test Supplier",
            "transaction_type": "PURCHASE",
            "is_active": True
        }
        client.post("/api/v1/inventory/transactions/", json=transaction_data)
    
    response = client.get("/api/v1/analytics/category-analysis/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert isinstance(data, list)
    assert "category" in data[0]
    assert "transaction_count" in data[0]
    assert "total_value" in data[0]

def test_product_performance(client):
    # Create some test transactions
    for i in range(3):
        transaction_data = {
            "product_id": f"PRD00{i}",
            "product_name": f"Test Product {i}",
            "category": "Electronics",
            "quantity": 10,
            "unit_price": 100.0,
            "supplier": "Test Supplier",
            "transaction_type": "SALE",
            "is_active": True
        }
        client.post("/api/v1/inventory/transactions/", json=transaction_data)
    
    response = client.get("/api/v1/analytics/product-performance/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert isinstance(data, list)
    assert "product_id" in data[0]
    assert "total_value" in data[0]