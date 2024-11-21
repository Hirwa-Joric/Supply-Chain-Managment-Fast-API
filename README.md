# Inventory Analytics System

A comprehensive inventory management and analytics system built with FastAPI, SQLAlchemy, and modern data science tools.

## Features

- **Inventory Management**
  - Track products, suppliers, and transactions
  - Monitor stock levels and reorder points
  - Handle different transaction types (purchase, sale, return, adjustment)

- **Analytics & Reporting**
  - Real-time analytics dashboard
  - Category-wise analysis
  - Product performance metrics
  - Supplier performance tracking
  - Stock turnover analysis

- **Data Processing**
  - Automated data preprocessing
  - Feature engineering
  - Data validation
  - Scalable data generation for testing

## Technology Stack

- **Backend**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Data Processing**: Pandas, NumPy, Scikit-learn
- **Testing**: Pytest
- **Documentation**: OpenAPI/Swagger

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/inventory-analytics.git
cd inventory-analytics
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Unix/MacOS
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your configurations
```

5. Initialize the database:
```bash
# Create database tables and initial data
python -m app.db.init_db
```

## Running the Application

1. Start the application:
```bash
# Development mode
uvicorn app.main:app --reload --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

2. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Inventory Management

- `POST /api/v1/inventory/transactions/`: Create new transaction
- `GET /api/v1/inventory/transactions/`: List transactions
- `GET /api/v1/inventory/transactions/{id}`: Get transaction details
- `POST /api/v1/inventory/products/`: Create new product
- `GET /api/v1/inventory/products/`: List products
- `PUT /api/v1/inventory/products/{id}`: Update product
- `GET /api/v1/inventory/stock-alerts/`: Get low stock alerts

### Analytics

- `GET /api/v1/analytics/summary/`: Get analytics summary
- `GET /api/v1/analytics/monthly-trends/`: Get monthly transaction trends
- `GET /api/v1/analytics/category-analysis/`: Get category-wise analysis
- `GET /api/v1/analytics/product-performance/`: Get product performance metrics
- `GET /api/v1/analytics/stock-turnover/`: Get stock turnover analysis
- `GET /api/v1/analytics/supplier-performance/`: Get supplier performance metrics

## Data Generation

Generate sample data for testing:

```bash
# Generate 1000 transaction records
python -m app.services.data_generator --records 1000
```

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api.py

# Run with coverage report
pytest --cov=app tests/
```

## Project Structure

```
inventory_analytics/
│
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── inventory.py
│   │   │   └── analytics.py
│   │   └── deps.py
│   ├── crud/
│   │   ├── base.py
│   │   └── crud_inventory.py
│   ├── models/
│   │   └── models.py
│   ├── schemas/
│   │   └── schemas.py
│   ├── services/
│   │   ├── data_generator.py
│   │   └── data_preprocessor.py
│   ├── main.py
│   └── config.py
│
├── tests/
│   ├── test_api.py
│   └── test_services.py
│
└── requirements.txt
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
