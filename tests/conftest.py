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

# Create tables in the database
Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a new database session with a rollback at the end of the test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def test_client(db_session):
    """Create a test client that uses the override_get_db fixture to return a session."""

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client


# Fixture to generate a user payload
@pytest.fixture()
def user_payload():
    """Generate a user payload"""
    return {
        "username": "kachi elite",
        "email": "kachi.elite@gmail.com",
        "phone_number": "2349069943111",
        "password": "Password1234",
        "role": "ADMIN",
        "is_active": True
    }


@pytest.fixture()
def bad_user_payload():
    """Generate a user payload"""
    return {
        "username": "kachi elite",
        "email": "kachi.elite@gmail.com",
        "phone_number": 2349069943111,
        "hash_password": "Password1234",
        "role": "SYS_ADMIN",
        "is_active": True
    }
