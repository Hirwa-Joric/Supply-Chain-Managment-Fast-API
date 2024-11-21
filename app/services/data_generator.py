import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import logging
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from app.models.models import InventoryTransaction, Product, Supplier
from app.crud.crud_inventory import CRUDProduct as crud_product
from app.crud.crud_inventory import CRUDSupplier as crud_supplier
logger = logging.getLogger(__name__)

class DataGenerator:
    def __init__(self):
        self.fake = Faker()
        self.categories = ['Electronics', 'Clothing', 'Food', 'Books', 'Furniture']
        self.transaction_types = ['PURCHASE', 'SALE', 'RETURN', 'ADJUSTMENT']
        
    def generate_dummy_data(
        self,
        num_records: int = 1000,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """Generate dummy transaction data"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=365)
        if not end_date:
            end_date = datetime.now()
            
        data = []
        for i in range(num_records):
            transaction = self._generate_single_transaction(i, start_date, end_date)
            data.append(transaction)
            
        df = pd.DataFrame(data)
        logger.info(f"Generated {num_records} dummy transactions")
        return df
        
    def _generate_single_transaction(
        self,
        index: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """Generate a single transaction record"""
        transaction_date = self.fake.date_time_between(start_date=start_date, end_date=end_date)
        quantity = random.randint(1, 100)
        unit_price = round(random.uniform(10, 1000), 2)
        
        return {
            'transaction_id': f'TRX{str(index+1).zfill(6)}',
            'product_id': f'PRD{str(random.randint(1, 100)).zfill(3)}',
            'product_name': self.fake.word() + ' ' + random.choice(['Tool', 'Part', 'Equipment']),
            'category': random.choice(self.categories),
            'quantity': quantity,
            'unit_price': unit_price,
            'total_value': round(quantity * unit_price, 2),
            'supplier': self.fake.company(),
            'transaction_type': random.choice(self.transaction_types),
            'transaction_date': transaction_date,
            'is_active': random.choice([True, True, True, False])  # Bias towards active
        }
        
    def generate_and_save_to_db(
        self,
        db: Session,
        num_records: int = 1000
    ) -> List[InventoryTransaction]:
        """Generate dummy data and save to database"""
        try:
            # Generate dummy data
            df = self.generate_dummy_data(num_records)
            
            # Convert to database records
            transactions = []
            for _, row in df.iterrows():
                transaction = InventoryTransaction(
                    transaction_id=row['transaction_id'],
                    product_id=row['product_id'],
                    product_name=row['product_name'],
                    category=row['category'],
                    quantity=row['quantity'],
                    unit_price=row['unit_price'],
                    total_value=row['total_value'],
                    supplier=row['supplier'],
                    transaction_type=row['transaction_type'],
                    transaction_date=row['transaction_date'],
                    is_active=row['is_active'],
                    year=row['transaction_date'].year,
                    month=row['transaction_date'].month,
                    day_of_week=row['transaction_date'].weekday()
                )
                transactions.append(transaction)
            
            # Save to database
            db.bulk_save_objects(transactions)
            db.commit()
            
            logger.info(f"Successfully saved {num_records} transactions to database")
            return transactions
            
        except Exception as e:
            logger.error(f"Error generating and saving data: {str(e)}")
            db.rollback()
            raise
            
    def generate_related_data(
        self,
        db: Session,
        num_products: int = 100,
        num_suppliers: int = 20
    ):
        """Generate related products and suppliers"""
        try:
            # Generate products
            products = []
            for i in range(num_products):
                product = Product(
                    product_id=f'PRD{str(i+1).zfill(3)}',
                    name=self.fake.word() + ' ' + random.choice(['Tool', 'Part', 'Equipment']),
                    category=random.choice(self.categories),
                    description=self.fake.text(max_nb_chars=200),
                    unit_price=round(random.uniform(10, 1000), 2),
                    stock_level=random.randint(0, 1000),
                    reorder_point=random.randint(10, 100)
                )
                products.append(product)
            
            # Generate suppliers
            suppliers = []
            for i in range(num_suppliers):
                supplier = Supplier(
                    supplier_id=f'SUP{str(i+1).zfill(3)}',
                    name=self.fake.company(),
                    contact_person=self.fake.name(),
                    email=self.fake.email(),
                    phone=self.fake.phone_number(),
                    address=self.fake.address(),
                    is_active=random.choice([True, True, True, False])
                )
                suppliers.append(supplier)
            
            # Save to database
            db.bulk_save_objects(products)
            db.bulk_save_objects(suppliers)
            db.commit()
            
            logger.info(f"Successfully generated {num_products} products and {num_suppliers} suppliers")
            
        except Exception as e:
            logger.error(f"Error generating related data: {str(e)}")
            db.rollback()
            raise

# Create generator instance
data_generator = DataGenerator()