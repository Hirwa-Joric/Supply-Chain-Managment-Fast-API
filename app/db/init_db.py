from sqlalchemy.orm import Session
import logging
from app.services.data_generator import data_generator
from app.database import init_db as init_database
from app.database import Base, engine
from app.models import models  # noqa: F401

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db(db: Session) -> None:
    try:
        # Create database tables
        Base.metadata.create_all(bind=engine)
        logger.info("Created database tables")
        
        # Generate initial data
        data_generator.generate_related_data(db, num_products=100, num_suppliers=20)
        data_generator.generate_and_save_to_db(db, num_records=1000)
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

def main() -> None:
    logger.info("Creating initial data")
    init_database()
    
    # Create db session
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()

if __name__ == "__main__":
    main()