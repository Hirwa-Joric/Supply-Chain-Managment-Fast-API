import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# Set up plotting style
plt.style.use('seaborn')
sns.set_palette("husl")

def load_data():
    """Load data from both IMS and OMS databases"""
    # Connect to IMS database
    ims_conn = sqlite3.connect('ims.db')
    
    # Get products data
    products_df = pd.read_sql_query("""
        SELECT 
            p.id as product_id,
            p.name as product_name,
            p.sku,
            p.description,
            p.unit_price,
            p.stock_quantity,
            p.reorder_point,
            p.category,
            p.supplier_id,
            p.created_at,
            s.name as supplier_name,
            s.email as supplier_email
        FROM products p
        LEFT JOIN suppliers s ON p.supplier_id = s.id
    """, ims_conn)
    
    # Connect to OMS database
    oms_conn = sqlite3.connect('oms.db')
    
    # Get orders data
    orders_df = pd.read_sql_query("""
        SELECT 
            o.id as order_id,
            o.customer_id,
            o.status,
            o.order_date,
            o.total_amount,
            o.shipping_address,
            c.name as customer_name,
            c.email as customer_email
        FROM orders o
        LEFT JOIN customers c ON o.customer_id = c.id
    """, oms_conn)
    
    # Get order items data
    order_items_df = pd.read_sql_query("""
        SELECT 
            oi.id as item_id,
            oi.order_id,
            oi.product_sku,
            oi.quantity,
            oi.unit_price,
            oi.total_price
        FROM order_items oi
    """, oms_conn)
    
    # Close connections
    ims_conn.close()
    oms_conn.close()
    
    return products_df, orders_df, order_items_df

def inventory_analysis(products_df):
    """Analyze inventory data"""
    print("\n=== Inventory Analysis ===")
    
    # Basic statistics
    print("\nProduct Statistics:")
    print(f"Total number of products: {len(products_df)}")
    print(f"Total inventory value: ${products_df['unit_price'].sum():,.2f}")
    print(f"Average product price: ${products_df['unit_price'].mean():,.2f}")
    
    # Category analysis
    print("\nCategory Distribution:")
    category_dist = products_df['category'].value_counts()
    print(category_dist)
    
    # Plot category distribution
    plt.figure(figsize=(12, 6))
    category_dist.plot(kind='bar')
    plt.title('Products by Category')
    plt.xlabel('Category')
    plt.ylabel('Number of Products')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    
    # Stock level analysis
    print("\nStock Level Analysis:")
    low_stock = products_df[products_df['stock_quantity'] <= products_df['reorder_point']]
    print(f"Products with low stock: {len(low_stock)}")
    
    # Plot stock distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(data=products_df, x='stock_quantity', bins=30)
    plt.title('Stock Quantity Distribution')
    plt.xlabel('Stock Quantity')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.show()

def order_analysis(orders_df, order_items_df, products_df):
    """Analyze order data"""
    print("\n=== Order Analysis ===")
    
    # Basic statistics
    print("\nOrder Statistics:")
    print(f"Total number of orders: {len(orders_df)}")
    print(f"Total revenue: ${orders_df['total_amount'].sum():,.2f}")
    print(f"Average order value: ${orders_df['total_amount'].mean():,.2f}")
    
    # Order status distribution
    print("\nOrder Status Distribution:")
    status_dist = orders_df['status'].value_counts()
    print(status_dist)
    
    # Plot order status distribution
    plt.figure(figsize=(10, 6))
    status_dist.plot(kind='pie', autopct='%1.1f%%')
    plt.title('Order Status Distribution')
    plt.axis('equal')
    plt.show()
    
    # Time series analysis
    orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
    daily_orders = orders_df.resample('D', on='order_date')['total_amount'].sum()
    
    plt.figure(figsize=(15, 6))
    daily_orders.plot()
    plt.title('Daily Order Revenue')
    plt.xlabel('Date')
    plt.ylabel('Revenue ($)')
    plt.tight_layout()
    plt.show()
    
    # Product performance
    merged_items = order_items_df.merge(products_df[['sku', 'name', 'category']], 
                                      left_on='product_sku', 
                                      right_on='sku')
    
    top_products = merged_items.groupby('name').agg({
        'quantity': 'sum',
        'total_price': 'sum'
    }).sort_values('total_price', ascending=False).head(10)
    
    print("\nTop 10 Products by Revenue:")
    print(top_products)
    
    # Plot top products
    plt.figure(figsize=(12, 6))
    top_products['total_price'].plot(kind='bar')
    plt.title('Top 10 Products by Revenue')
    plt.xlabel('Product')
    plt.ylabel('Revenue ($)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def customer_analysis(orders_df):
    """Analyze customer behavior"""
    print("\n=== Customer Analysis ===")
    
    # Customer order frequency
    customer_orders = orders_df.groupby('customer_id').agg({
        'order_id': 'count',
        'total_amount': 'sum'
    }).rename(columns={'order_id': 'order_count'})
    
    print("\nCustomer Statistics:")
    print(f"Total customers: {len(customer_orders)}")
    print(f"Average orders per customer: {customer_orders['order_count'].mean():.2f}")
    print(f"Average customer lifetime value: ${customer_orders['total_amount'].mean():,.2f}")
    
    # Plot customer order distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(data=customer_orders, x='order_count', bins=30)
    plt.title('Customer Order Frequency Distribution')
    plt.xlabel('Number of Orders')
    plt.ylabel('Number of Customers')
    plt.tight_layout()
    plt.show()

def main():
    # Load data
    print("Loading data...")
    products_df, orders_df, order_items_df = load_data()
    
    # Perform analysis
    inventory_analysis(products_df)
    order_analysis(orders_df, order_items_df, products_df)
    customer_analysis(orders_df)

if __name__ == "__main__":
    main()
