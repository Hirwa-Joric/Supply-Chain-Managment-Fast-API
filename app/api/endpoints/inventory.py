from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import crud, schemas
from app.api import deps
from datetime import datetime

router = APIRouter()

@router.post("/transactions/", response_model=schemas.Transaction)
def create_transaction(
    *,
    db: Session = Depends(deps.get_db),
    transaction_in: schemas.TransactionCreate,
):
    """Create new transaction"""
    transaction = crud.transaction.create_with_analytics(db=db, obj_in=transaction_in)
    return transaction

@router.get("/transactions/", response_model=List[schemas.Transaction])
def list_transactions(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
):
    """List transactions with optional filtering"""
    query = db.query(crud.transaction.model)
    
    if category:
        query = query.filter(crud.transaction.model.category == category)
    if start_date:
        query = query.filter(crud.transaction.model.transaction_date >= start_date)
    if end_date:
        query = query.filter(crud.transaction.model.transaction_date <= end_date)
        
    transactions = query.offset(skip).limit(limit).all()
    return transactions

@router.get("/transactions/{transaction_id}", response_model=schemas.Transaction)
def get_transaction(
    transaction_id: str,
    db: Session = Depends(deps.get_db),
):
    """Get specific transaction by ID"""
    transaction = crud.transaction.get_by_attribute(db, "transaction_id", transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.post("/products/", response_model=schemas.Product)
def create_product(
    *,
    db: Session = Depends(deps.get_db),
    product_in: schemas.ProductCreate,
):
    """Create new product"""
    product = crud.product.create(db=db, obj_in=product_in)
    return product

@router.get("/products/", response_model=List[schemas.Product])
def list_products(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
):
    """List products with optional category filter"""
    query = db.query(crud.product.model)
    if category:
        query = query.filter(crud.product.model.category == category)
    products = query.offset(skip).limit(limit).all()
    return products

@router.put("/products/{product_id}", response_model=schemas.Product)
def update_product(
    *,
    db: Session = Depends(deps.get_db),
    product_id: str,
    product_in: schemas.ProductUpdate,
):
    """Update product"""
    product = crud.product.get_by_attribute(db, "product_id", product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product = crud.product.update(db=db, db_obj=product, obj_in=product_in)
    return product

@router.post("/suppliers/", response_model=schemas.Supplier)
def create_supplier(
    *,
    db: Session = Depends(deps.get_db),
    supplier_in: schemas.SupplierCreate,
):
    """Create new supplier"""
    supplier = crud.supplier.create(db=db, obj_in=supplier_in)
    return supplier

@router.get("/suppliers/", response_model=List[schemas.Supplier])
def list_suppliers(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
):
    """List suppliers"""
    if active_only:
        suppliers = crud.supplier.get_active_suppliers(db, skip=skip, limit=limit)
    else:
        suppliers = crud.supplier.get_multi(db, skip=skip, limit=limit)
    return suppliers

@router.put("/suppliers/{supplier_id}", response_model=schemas.Supplier)
def update_supplier(
    *,
    db: Session = Depends(deps.get_db),
    supplier_id: str,
    supplier_in: schemas.SupplierUpdate,
):
    """Update supplier"""
    supplier = crud.supplier.get_by_attribute(db, "supplier_id", supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    supplier = crud.supplier.update(db=db, db_obj=supplier, obj_in=supplier_in)
    return supplier

@router.get("/stock-alerts/", response_model=List[schemas.Product])
def get_stock_alerts(
    db: Session = Depends(deps.get_db),
):
    """Get products that need reordering"""
    products = db.query(crud.product.model)\
        .filter(crud.product.model.stock_level <= crud.product.model.reorder_point)\
        .all()
    return products