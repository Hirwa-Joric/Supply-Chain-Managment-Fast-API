# Supply Chain Management API

A FastAPI-based REST API for managing supply chain operations.

## Features

- Inventory Management
- Order Processing
- Supplier Management
- Product Tracking
- Real-time Stock Updates

## Technology Stack

- Python 3.8+
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic

## Installation

1. Clone the repository:
   ```bash
   git clone git@github.com:Hirwa-Joric/Supply-Chain-Managment-Fast-API.git
   cd Supply-Chain-Managment-Fast-API
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

## API Documentation

Once the server is running, access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
