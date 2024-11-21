from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import crud, schemas
from app.api import deps
from app.models.models import InventoryTransaction, Product, Supplier
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/summary/", response_model=schemas.AnalyticsSummary)
def get_analytics_summary(
    db: Session = Depends(deps.get_db),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    category: Optional[str] = None,
):
    """Get analytics summary"""
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()

    return crud.transaction.get_analytics(
        db=db,
        start_date=start_date,
        end_date=end_date,
        category=category
    )

@router.get("/monthly-trends/")
def get_monthly_trends(
    db: Session = Depends(deps.get_db),
    months: int = 12,
):
    """Get monthly transaction trends"""
    start_date = datetime.utcnow() - timedelta(days=months * 30)
    
    trends = db.query(
        func.date_trunc('month', InventoryTransaction.transaction_date).label('month'),
        func.sum(InventoryTransaction.total_value).label('total_value'),
        func.count(InventoryTransaction.id).label('transaction_count')
    ).filter(
        InventoryTransaction.transaction_date >= start_date
    ).group_by(
        'month'
    ).order_by(
        'month'
    ).all()
    
    return [
        {
            "month": month.strftime("%Y-%m"),
            "total_value": float(total_value),
            "transaction_count": transaction_count
        }
        for month, total_value, transaction_count in trends
    ]

@router.get("/category-analysis/")
def get_category_analysis(
    db: Session = Depends(deps.get_db),
):
    """Get detailed category analysis"""
    categories = db.query(
        InventoryTransaction.category,
        func.count(InventoryTransaction.id).label('transaction_count'),
        func.sum(InventoryTransaction.total_value).label('total_value'),
        func.avg(InventoryTransaction.unit_price).label('avg_price')
    ).group_by(
        InventoryTransaction.category
    ).all()
    
    return [
        {
            "category": category,
            "transaction_count": transaction_count,
            "total_value": float(total_value),
            "average_price": float(avg_price)
        }
        for category, transaction_count, total_value, avg_price in categories
    ]

@router.get("/product-performance/")
def get_product_performance(
    db: Session = Depends(deps.get_db),
    top_n: int = 10,
):
    """Get top performing products"""
    products = db.query(
        InventoryTransaction.product_id,
        InventoryTransaction.product_name,
        func.count(InventoryTransaction.id).label('transaction_count'),
        func.sum(InventoryTransaction.total_value).label('total_value')
    ).group_by(
        InventoryTransaction.product_id,
        InventoryTransaction.product_name
    ).order_by(
        func.sum(InventoryTransaction.total_value).desc()
    ).limit(top_n).all()
    
    return [
        {
            "product_id": product_id,
            "product_name": product_name,
            "transaction_count": transaction_count,
            "total_value": float(total_value)
        }
        for product_id, product_name, transaction_count, total_value in products
    ]

@router.get("/stock-turnover/")
def get_stock_turnover(
    db: Session = Depends(deps.get_db),
):
    """Calculate stock turnover rates"""
    current_date = datetime.utcnow()
    start_date = current_date - timedelta(days=365)
    
    products = db.query(Product).all()
    turnover_rates = []
    
    for product in products:
        sales = db.query(
            func.sum(InventoryTransaction.quantity)
        ).filter(
            InventoryTransaction.product_id == product.product_id,
            InventoryTransaction.transaction_type == 'SALE',
            InventoryTransaction.transaction_date >= start_date
        ).scalar() or 0
        
        if product.stock_level > 0:
            turnover_rate = sales / product.stock_level
        else:
            turnover_rate = 0
            
        turnover_rates.append({
            "product_id": product.product_id,
            "product_name": product.name,
            "stock_level": product.stock_level,
            "annual_sales": sales,
            "turnover_rate": float(turnover_rate)
        })
    
    return sorted(turnover_rates, key=lambda x: x['turnover_rate'], reverse=True)

@router.get("/supplier-performance/")
def get_supplier_performance(
    db: Session = Depends(deps.get_db),
):
    """Analyze supplier performance"""
    suppliers = db.query(
        InventoryTransaction.supplier,
        func.count(InventoryTransaction.id).label('transaction_count'),
        func.sum(InventoryTransaction.total_value).label('total_value'),
        func.avg(InventoryTransaction.unit_price).label('avg_price')
    ).group_by(
        InventoryTransaction.supplier
    ).all()
    
    return [
        {
            "supplier": supplier,
            "transaction_count": transaction_count,
            "total_value": float(total_value),
            "average_price": float(avg_price)
        }
        for supplier, transaction_count, total_value, avg_price in suppliers
    ]