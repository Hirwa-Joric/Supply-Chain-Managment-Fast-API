from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URLs
IMS_DATABASE_URL = "sqlite:///./ims.db"
OMS_DATABASE_URL = "sqlite:///./oms.db"

# Create engines
ims_engine = create_engine(
    IMS_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

oms_engine = create_engine(
    OMS_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create sessions
IMSSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ims_engine)
OMSSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=oms_engine)

# Create base class for models
Base = declarative_base()

# Database dependency functions
def get_ims_db():
    db = IMSSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_oms_db():
    db = OMSSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize databases
def init_db():
    from models import Product, Supplier, Customer, Order, OrderItem
    Base.metadata.create_all(bind=ims_engine)  # Create IMS tables
    Base.metadata.create_all(bind=oms_engine)  # Create OMS tables
