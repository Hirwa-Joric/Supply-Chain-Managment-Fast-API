import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from app.services.data_generator import DataGenerator
from app.services.data_preprocessor import DataPreprocessor
from sqlalchemy.orm import Session
from app.database import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_service.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def data_generator():
    return DataGenerator()

@pytest.fixture
def data_preprocessor():
    return DataPreprocessor()

def test_data_generator_create_dummy_data(data_generator):
    num_records = 100
    df = data_generator.generate_dummy_data(num_records)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == num_records
    assert all(col in df.columns for col in [
        'transaction_id', 'product_id', 'product_name', 'category',
        'quantity', 'unit_price', 'total_value', 'supplier',
        'transaction_type', 'transaction_date', 'is_active'
    ])

def test_data_generator_date_range(data_generator):
    start_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now()
    df = data_generator.generate_dummy_data(
        num_records=100,
        start_date=start_date,
        end_date=end_date
    )
    
    assert all(
        start_date <= pd.to_datetime(date) <= end_date
        for date in df['transaction_date']
    )

def test_data_preprocessor_handle_missing_values(data_preprocessor):
    # Create sample data with missing values
    data = pd.DataFrame({
        'quantity': [1, np.nan, 3, 4],
        'unit_price': [10.0, 20.0, np.nan, 40.0],
        'category': ['A', None, 'C', 'D']
    })
    
    processed_df = data_preprocessor._handle_missing_values(data)
    
    assert not processed_df.isnull().any().any()
    assert isinstance(processed_df, pd.DataFrame)

def test_data_preprocessor_encode_categorical_variables(data_preprocessor):
    data = pd.DataFrame({
        'category': ['A', 'B', 'A', 'C'],
        'supplier': ['X', 'Y', 'X', 'Z'],
        'transaction_type': ['SALE', 'PURCHASE', 'SALE', 'RETURN']
    })
    
    processed_df = data_preprocessor._encode_categorical_variables(data)
    
    assert 'category_encoded' in processed_df.columns
    assert 'supplier_encoded' in processed_df.columns
    assert 'transaction_type_encoded' in processed_df.columns

def test_data_preprocessor_scale_numerical_features(data_preprocessor):
    data = pd.DataFrame({
        'quantity': [1, 2, 3, 4],
        'unit_price': [10.0, 20.0, 30.0, 40.0],
        'total_value': [10.0, 40.0, 90.0, 160.0]
    })
    
    processed_df = data_preprocessor._scale_numerical_features(data)
    
    assert 'quantity_scaled' in processed_df.columns
    assert 'unit_price_scaled' in processed_df.columns
    assert 'total_value_scaled' in processed_df.columns

def test_data_preprocessor_add_derived_features(data_preprocessor, db):
    # Create sample data
    data = pd.DataFrame({
        'transaction_id': ['T1', 'T2', 'T3', 'T4'],
        'product_id': ['P1', 'P1', 'P2', 'P2'],
        'unit_price': [10.0, 20.0, 30.0, 40.0],
        'transaction_date': pd.date_range(start='2023-01-01', periods=4),
        'category': ['A', 'A', 'B', 'B']
    })
    
    processed_df = data_preprocessor._add_derived_features(data, db)
    
    assert 'year' in processed_df.columns
    assert 'month' in processed_df.columns
    assert 'day_of_week' in processed_df.columns
    assert 'is_weekend' in processed_df.columns
    assert 'transactions_per_product' in processed_df.columns

def test_generate_and_save_to_db(data_generator, db):
    num_records = 10
    transactions = data_generator.generate_and_save_to_db(db, num_records)
    
    assert len(transactions) == num_records
    
    # Verify data was saved to database
    from app.models.models import InventoryTransaction
    db_transactions = db.query(InventoryTransaction).all()
    assert len(db_transactions) == num_records

def test_generate_related_data(data_generator, db):
    num_products = 5
    num_suppliers = 3
    data_generator.generate_related_data(db, num_products, num_suppliers)
    
    # Verify products were created
    from app.models.models import Product
    products = db.query(Product).all()
    assert len(products) == num_products
    
    # Verify suppliers were created
    from app.models.models import Supplier
    suppliers = db.query(Supplier).all()
    assert len(suppliers) == num_suppliers

def test_complete_preprocessing_pipeline(data_generator, data_preprocessor, db):
    # Generate data
    raw_data = data_generator.generate_dummy_data(num_records=50)
    
    # Preprocess data
    processed_data = data_preprocessor.preprocess_transaction_data(db, raw_data)
    
    # Verify all expected features are present
    expected_features = [
        'quantity_scaled', 'unit_price_scaled', 'total_value_scaled',
        'category_encoded', 'supplier_encoded', 'transaction_type_encoded',
        'year', 'month', 'day_of_week', 'is_weekend',
        'price_vs_category_avg', 'transactions_per_product'
    ]
    
    assert all(feature in processed_data.columns for feature in expected_features)
    assert not processed_data.isnull().any().any()