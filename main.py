from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
import pandas as pd
from typing import List, Dict, Any

from database import get_ims_db, get_oms_db, init_db
from models import Product, Supplier, Customer, Order, OrderItem
import schemas
from generate_data import generate_sample_data

app = FastAPI(
    title="Supply Chain Management API",
    description="API for managing supply chain data including inventory and orders",
    version="1.0.0"
)

# Initialize database tables on startup
@app.on_event("startup")
async def startup_event():
    init_db()

# Data Management Endpoints
@app.post("/api/generate-data")
async def generate_data():
    """Generate sample data for both IMS and OMS databases"""
    try:
        generate_sample_data()
        return {"message": "Sample data generated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/clear-data")
async def clear_data(
    ims_db: Session = Depends(get_ims_db),
    oms_db: Session = Depends(get_oms_db)
):
    """Clear all data from both databases"""
    try:
        # Clear IMS tables
        ims_db.query(Product).delete()
        ims_db.query(Supplier).delete()
        ims_db.commit()
        
        # Clear OMS tables
        oms_db.query(OrderItem).delete()
        oms_db.query(Order).delete()
        oms_db.query(Customer).delete()
        oms_db.commit()
        
        return {"message": "All data cleared successfully"}
    except Exception as e:
        ims_db.rollback()
        oms_db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Inventory Management Endpoints
@app.get("/api/inventory", response_model=List[schemas.Product])
async def get_inventory(db: Session = Depends(get_ims_db)):
    """Get all products in inventory"""
    return db.query(Product).all()

@app.get("/api/inventory/{product_id}", response_model=schemas.Product)
async def get_product(product_id: int, db: Session = Depends(get_ims_db)):
    """Get specific product details"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.get("/api/suppliers", response_model=List[schemas.Supplier])
async def get_suppliers(db: Session = Depends(get_ims_db)):
    """Get all suppliers"""
    return db.query(Supplier).all()

@app.get("/api/inventory/low-stock", response_model=List[schemas.Product])
async def get_low_stock_products(db: Session = Depends(get_ims_db)):
    """Get products with stock below reorder point"""
    return db.query(Product).filter(Product.stock_quantity <= Product.reorder_point).all()

# Order Management Endpoints
@app.get("/api/orders", response_model=List[schemas.Order])
async def get_orders(db: Session = Depends(get_oms_db)):
    """Get all orders"""
    return db.query(Order).all()

@app.get("/api/orders/{order_id}", response_model=schemas.Order)
async def get_order(order_id: int, db: Session = Depends(get_oms_db)):
    """Get specific order details"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.get("/api/customers", response_model=List[schemas.Customer])
async def get_customers(db: Session = Depends(get_oms_db)):
    """Get all customers"""
    return db.query(Customer).all()

# Analytics Endpoints
@app.get("/analytics/inventory", response_model=schemas.InventoryAnalytics)
async def get_inventory_analytics(db: Session = Depends(get_ims_db)):
    """Get inventory analytics"""
    products = db.query(Product).all()
    df = pd.DataFrame([{
        'id': p.id,
        'category': p.category,
        'unit_price': p.unit_price,
        'stock_quantity': p.stock_quantity,
        'reorder_point': p.reorder_point
    } for p in products])
    
    analytics = {
        'total_products': len(products),
        'total_value': float(df['unit_price'].sum()),
        'low_stock_items': int(df[df['stock_quantity'] <= df['reorder_point']].count()),
        'categories_distribution': df['category'].value_counts().to_dict(),
        'avg_price_by_category': df.groupby('category')['unit_price'].mean().to_dict()
    }
    
    return analytics

@app.get("/analytics/orders", response_model=schemas.OrderAnalytics)
async def get_order_analytics(
    oms_db: Session = Depends(get_oms_db),
    ims_db: Session = Depends(get_ims_db)
):
    """Get order analytics"""
    orders = oms_db.query(Order).all()
    order_items = oms_db.query(OrderItem).all()
    
    orders_df = pd.DataFrame([{
        'id': o.id,
        'status': o.status,
        'total_amount': o.total_amount
    } for o in orders])
    
    items_df = pd.DataFrame([{
        'product_sku': i.product_sku,
        'quantity': i.quantity,
        'total_price': i.total_price
    } for i in order_items])
    
    analytics = {
        'total_orders': len(orders),
        'total_revenue': float(orders_df['total_amount'].sum()),
        'avg_order_value': float(orders_df['total_amount'].mean()),
        'orders_by_status': orders_df['status'].value_counts().to_dict(),
        'top_selling_products': items_df.groupby('product_sku').agg({
            'quantity': 'sum',
            'total_price': 'sum'
        }).sort_values('quantity', ascending=False).head(10).to_dict('records')
    }
    
    return analytics

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
