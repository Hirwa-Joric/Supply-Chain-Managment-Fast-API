from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime
from app.models.models import InventoryTransaction, Product, Supplier, AnalyticsSnapshot
from app.schemas import schemas
from app.crud.base import CRUDBase

class CRUDTransaction(CRUDBase[InventoryTransaction, schemas.TransactionCreate, schemas.TransactionUpdate]):
    def create_with_analytics(
        self, db: Session, *, obj_in: schemas.TransactionCreate
    ) -> InventoryTransaction:
        # Calculate analytics fields
        year = datetime.utcnow().year
        month = datetime.utcnow().month
        day_of_week = datetime.utcnow().weekday()
        
        # Get average price per category
        avg_price = db.query(func.avg(InventoryTransaction.unit_price))\
            .filter(InventoryTransaction.category == obj_in.category)\
            .scalar() or obj_in.unit_price
            
        # Get transactions per product
        transactions_count = db.query(func.count(InventoryTransaction.id))\
            .filter(InventoryTransaction.product_id == obj_in.product_id)\
            .scalar() or 0
        
        # Create transaction object
        db_obj = InventoryTransaction(
            **obj_in.dict(),
            total_value=obj_in.quantity * obj_in.unit_price,
            year=year,
            month=month,
            day_of_week=day_of_week,
            avg_price_per_category=avg_price,
            transactions_per_product=transactions_count + 1
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_analytics(
        self,
        db: Session,
        *,
        start_date: datetime,
        end_date: datetime,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        query = db.query(InventoryTransaction)
        
        if category:
            query = query.filter(InventoryTransaction.category == category)
            
        query = query.filter(
            and_(
                InventoryTransaction.transaction_date >= start_date,
                InventoryTransaction.transaction_date <= end_date
            )
        )
        
        total_transactions = query.count()
        total_value = query.with_entities(
            func.sum(InventoryTransaction.total_value)
        ).scalar() or 0
        
        return {
            "total_transactions": total_transactions,
            "total_value": float(total_value),
            "avg_transaction_value": float(total_value / total_transactions if total_transactions else 0),
            "category_distribution": self.get_category_distribution(db, start_date, end_date),
            "transaction_type_distribution": self.get_transaction_type_distribution(db, start_date, end_date)
        }

    def get_category_distribution(
        self,
        db: Session,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, int]:
        result = db.query(
            InventoryTransaction.category,
            func.count(InventoryTransaction.id)
        ).filter(
            and_(
                InventoryTransaction.transaction_date >= start_date,
                InventoryTransaction.transaction_date <= end_date
            )
        ).group_by(InventoryTransaction.category).all()
        
        return {category: count for category, count in result}

    def get_transaction_type_distribution(
        self,
        db: Session,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, int]:
        result = db.query(
            InventoryTransaction.transaction_type,
            func.count(InventoryTransaction.id)
        ).filter(
            and_(
                InventoryTransaction.transaction_date >= start_date,
                InventoryTransaction.transaction_date <= end_date
            )
        ).group_by(InventoryTransaction.transaction_type).all()
        
        return {tx_type: count for tx_type, count in result}

class CRUDProduct(CRUDBase[Product, schemas.ProductCreate, schemas.ProductUpdate]):
    def update_stock_level(
        self,
        db: Session,
        *,
        product_id: str,
        quantity_change: int
    ) -> Product:
        product = db.query(Product).filter(Product.product_id == product_id).first()
        if product:
            product.stock_level += quantity_change
            db.commit()
            db.refresh(product)
        return product

class CRUDSupplier(CRUDBase[Supplier, schemas.SupplierCreate, schemas.SupplierUpdate]):
    def get_active_suppliers(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Supplier]:
        return db.query(Supplier)\
            .filter(Supplier.is_active == True)\
            .offset(skip)\
            .limit(limit)\
            .all()

# Create crud instances
transaction = CRUDTransaction(InventoryTransaction)
product = CRUDProduct(Product)
supplier = CRUDSupplier(Supplier)