# Supply Chain Management API

A comprehensive API for managing supply chain data, including inventory and order management systems.

## Features

- **Inventory Management System (IMS)**
  - Product management
  - Supplier management
  - Stock tracking
  - Category-based organization
  - Reorder point monitoring

- **Order Management System (OMS)**
  - Customer management
  - Order processing
  - Order status tracking
  - Order items management
  - Shipping information

- **Analytics**
  - Inventory analytics
  - Order analytics
  - Sales performance metrics
  - Stock level monitoring
  - Category distribution analysis

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd scm_api
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. Generate sample data:
```bash
curl -X POST http://localhost:8000/api/clear-data    # Clear existing data
curl -X POST http://localhost:8000/api/generate-data  # Generate new data
```

3. Access the API endpoints:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Data Analysis and Preprocessing

### Using Jupyter Notebook
The project includes a Jupyter notebook (`data_analysis.ipynb`) for data analysis and visualization. To use it:

1. Start Jupyter:
```bash
jupyter notebook
```

2. Open `data_analysis.ipynb` in your browser

3. The notebook includes:
   - Data loading from both databases
   - Data preprocessing and cleaning
   - Exploratory data analysis
   - Statistical analysis
   - Visualizations

### Analysis Template
We also provide `analysis_template.py` as a reference implementation that includes:
- Database connection setup
- Data loading and preprocessing functions
- Inventory analysis
- Order analysis
- Customer behavior analysis
- Visualization examples

You can use this template to:
- Create your own analysis scripts
- Modify the Jupyter notebook
- Build custom analytics dashboards

## API Endpoints

### Data Management
- `POST /api/generate-data` - Generate sample data
- `POST /api/clear-data` - Clear all data

### Inventory Management
- `GET /api/processed-inventory-data` - Get processed inventory data
- `GET /api/inventory/{product_id}` - Get specific product details
- `GET /api/suppliers` - List all suppliers
- `GET /api/inventory/low-stock` - Get products below reorder point

### Order Management
- `GET /api/processed-order-data` - Get processed order data
- `GET /api/orders/{order_id}` - Get specific order details
- `GET /api/customers` - List all customers

### Analytics
- `GET /analytics/inventory` - Get inventory analytics
- `GET /analytics/orders` - Get order analytics
- `GET /analytics/sales` - Get sales performance metrics

## Data Models

### IMS Models
- Product
- Supplier

### OMS Models
- Customer
- Order
- OrderItem

## Database Structure

The system uses two SQLite databases:
- `ims.db` - Inventory Management System database
- `oms.db` - Order Management System database

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
