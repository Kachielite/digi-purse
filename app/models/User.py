from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, event, Boolean, Enum

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    hash_password = Column(String, nullable=False)
    role = Column(Enum("SYS_ADMIN", "ADMIN", "USER", name="role"), nullable=False)
    is_active = Column(Boolean)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # Corrected


@event.listens_for(User, "before_update")
def receive_before_update(mapper, connection, target):
    target.updated_at = datetime.now()
