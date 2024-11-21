import uvicorn
import click
import logging
from app.database import init_db
from app.services.data_generator import data_generator
from app.database import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.group()
def cli():
    """Inventory Analytics System Management CLI"""
    pass

@cli.command()
@click.option('--host', default='0.0.0.0', help='Host to bind.')
@click.option('--port', default=8000, help='Port to bind.')
@click.option('--reload', is_flag=True, help='Enable auto-reload.')
def serve(host, port, reload):
    """Start the FastAPI server"""
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

@cli.command()
@click.option('--records', default=1000, help='Number of records to generate.')
def generate_data(records):
    """Generate sample data"""
    logger.info(f"Generating {records} sample records")
    db = SessionLocal()
    try:
        # Initialize database
        init_db()
        
        # Generate data
        data_generator.generate_related_data(db)
        data_generator.generate_and_save_to_db(db, records)
        
        logger.info("Data generation completed successfully")
    except Exception as e:
        logger.error(f"Error generating data: {str(e)}")
        raise
    finally:
        db.close()

@cli.command()
def init():
    """Initialize the database"""
    logger.info("Initializing database")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

@cli.command()
def test():
    """Run tests"""
    import pytest
    pytest.main(["-v", "tests/"])

if __name__ == '__main__':
    cli()