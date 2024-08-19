import pytest
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.db.base import Base
from app.db.session import get_db
from app.main import app

# SQL DB for testing
SQL_LITE_DB_URL = 'sqlite:///./testdb.db'

# Create a SQLAlchemy engine
engine = create_engine(SQL_LITE_DB_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)

# Create a session maker to manage sessions
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    # Create the tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)  # Clean up the database after each test


# Fixture to generate a user payload
@pytest.fixture()
def user_payload():
    """Generate a user payload"""
    return {
        "username": "kachi elite",
        "email": "kachi.elite@mail.com",
        "phone_number": "2349069943111",
        "password": "Password1234",
        "role": "ADMIN",
        "is_active": True
    }
