from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Base class for models
Base = declarative_base()

# SQLite database file
DATABASE_URL = "sqlite:///media.db"

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Helper to get a session
def get_session():
    return SessionLocal()
