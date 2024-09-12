import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.crud.crud_auth import get_current_user
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


@pytest.fixture(scope="function")
def override_get_current_user(db_session):
    """Override the get_current_user dependency to use the db_session."""

    def _override_get_current_user(token: str, db=db_session):
        status_code, user = get_current_user(token, db)
        if status_code != 200:
            raise HTTPException(status_code=status_code, detail=user["message"])
        return user

    app.dependency_overrides[get_current_user] = _override_get_current_user
    yield
    app.dependency_overrides.pop(get_current_user, None)


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
def admin_user_payload():
    """Generate a user payload"""
    return {
        "username": "Micheal Gabriel",
        "email": "micheal@gmail.com",
        "phone_number": "2349069943120",
        "password": "Password1234",
        "role": "ADMIN",
        "is_active": True
    }


@pytest.fixture()
def sys_user_payload():
    """Generate a sys user payload"""
    return {
        "username": "John Doe",
        "email": "john.doe@gmail.com",
        "phone_number": "2349069943112",
        "password": "Password1234",
        "role": "SYS_ADMIN",
        "is_active": True
    }


@pytest.fixture()
def normal_user_payload():
    """Generate a normal user payload"""
    return {
        "username": "Paul Doe",
        "email": "paul.doe@gmail.com",
        "phone_number": "2349069943113",
        "password": "Password1234",
        "role": "USER",
        "is_active": True
    }


@pytest.fixture()
def user_payload_existing_email():
    """Generate a user payload"""
    return {
        "username": "Jack Doe",
        "email": "kachi.elite@gmail.com",
        "phone_number": "2349069943114",
        "password": "Password1234",
        "role": "ADMIN",
        "is_active": True
    }


@pytest.fixture()
def user_payload_existing_phone_number():
    """Generate a user payload"""
    return {
        "username": "Jack Doe",
        "email": "kachi1.elite@gmail.com",
        "phone_number": "2349069943111",
        "password": "Password1234",
        "role": "ADMIN",
        "is_active": True
    }


@pytest.fixture()
def user_payload_existing_username():
    """Generate a user payload"""
    return {
        "username": "kachi elite",
        "email": "kachi2.elite@gmail.com",
        "phone_number": "2349069943118",
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


@pytest.fixture()
def user_update_payload():
    """Generate a user update payload"""
    return {
        "role": "ADMIN",
        "is_active": False,
    }


@pytest.fixture()
def credit_transaction_payload():
    """Generate a credit transaction"""
    return {
          "amount": 100,
          "destination": "2349069943113",
          "source": "TOP UP",
          "type": "credit"
    }


@pytest.fixture()
def debit_transaction_payload():
    """Generate a credit transaction"""
    return {
          "amount": 100,
          "destination": "2349069943113",
          "source": "SERVICE",
          "type": "debit"
    }


@pytest.fixture()
def sys_user_debit_transaction_payload():
    """Generate a credit transaction"""
    return {
          "amount": 100,
          "destination": "2349069943112",
          "source": "SERVICE",
          "type": "debit"
    }


@pytest.fixture()
def block_wallet_request():
    """Generate a credit transaction"""
    return {
          "is_blocked": True,
    }


@pytest.fixture()
def credit_transaction_payload_for_loyalty():
    """Generate a credit transaction"""
    return {
          "amount": 10000,
          "destination": "2349069943113",
          "source": "TOP UP",
          "type": "credit"
    }


@pytest.fixture()
def debit_transaction_payload_for_loyalty():
    """Generate a credit transaction"""
    return {
          "amount": 1000,
          "destination": "2349069943113",
          "source": "SERVICE",
          "type": "debit"
    }

