from faker import Faker
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import Product, Supplier, Customer, Order, OrderItem
from database import get_ims_db, get_oms_db

fake = Faker()

def generate_suppliers(db: Session, count: int = 50):
    suppliers = []
    for _ in range(count):
        supplier = Supplier(
            name=fake.company(),
            contact_person=fake.name(),
            email=fake.unique.company_email(),
            phone=fake.phone_number(),
            address=fake.address()
        )
        suppliers.append(supplier)
    
    db.add_all(suppliers)
    db.commit()
    return suppliers

def generate_products(db: Session, suppliers: list, count: int = 200):
    categories = ['Electronics', 'Clothing', 'Food', 'Furniture', 'Books', 'Sports', 'Tools', 'Toys']
    products = []
    
    for _ in range(count):
        price = round(random.uniform(10, 1000), 2)
        product = Product(
            name=fake.product_name(),
            sku=fake.unique.ean13(),
            description=fake.text(max_nb_chars=200),
            unit_price=price,
            stock_quantity=random.randint(0, 1000),
            reorder_point=random.randint(10, 100),
            category=random.choice(categories),
            supplier_id=random.choice(suppliers).id
        )
        products.append(product)
    
    db.add_all(products)
    db.commit()
    return products

def generate_customers(db: Session, count: int = 100):
    customers = []
    for _ in range(count):
        customer = Customer(
            name=fake.name(),
            email=fake.unique.email(),
            phone=fake.phone_number(),
            address=fake.address()
        )
        customers.append(customer)
    
    db.add_all(customers)
    db.commit()
    return customers

def generate_orders(db: Session, customers: list, ims_db: Session, count: int = 300):
    orders = []
    order_items = []
    
    # Get all products from IMS
    products = ims_db.query(Product).all()
    
    for _ in range(count):
        # Create order
        order_date = fake.date_time_between(start_date='-1y', end_date='now')
        status = random.choice(['pending', 'processing', 'shipped', 'delivered', 'cancelled'])
        
        order = Order(
            customer_id=random.choice(customers).id,
            status=status,
            order_date=order_date,
            shipping_address=fake.address(),
            total_amount=0  # Will be calculated from items
        )
        db.add(order)
        db.flush()  # Get order ID
        
        # Create 1-5 order items
        total_amount = 0
        for _ in range(random.randint(1, 5)):
            product = random.choice(products)
            quantity = random.randint(1, 10)
            total_price = quantity * product.unit_price
            total_amount += total_price
            
            order_item = OrderItem(
                order_id=order.id,
                product_sku=product.sku,
                quantity=quantity,
                unit_price=product.unit_price,
                total_price=total_price
            )
            order_items.append(order_item)
        
        order.total_amount = total_amount
        orders.append(order)
    
    db.add_all(order_items)
    db.commit()
    return orders

def generate_sample_data():
    # Get database sessions
    ims_db = next(get_ims_db())
    oms_db = next(get_oms_db())
    
    try:
        # Generate IMS data
        print("Generating suppliers...")
        suppliers = generate_suppliers(ims_db)
        
        print("Generating products...")
        products = generate_products(ims_db, suppliers)
        
        # Generate OMS data
        print("Generating customers...")
        customers = generate_customers(oms_db)
        
        print("Generating orders...")
        orders = generate_orders(oms_db, customers, ims_db)
        
        print("Sample data generation completed successfully!")
        
    except Exception as e:
        print(f"Error generating sample data: {str(e)}")
        ims_db.rollback()
        oms_db.rollback()
        raise
    
    finally:
        ims_db.close()
        oms_db.close()

if __name__ == "__main__":
    generate_sample_data()
