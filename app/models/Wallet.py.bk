import uuid
from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime, event
from sqlalchemy.dialects.postgresql import UUID as pgUUID

from app.db.base import Base


class Wallet(Base):
    __tablename__ = "wallet"

    id = Column(pgUUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


@event.listens_for(Wallet, 'before_update')
def receive_before_update(mapper, connection, target):
    target.updated_at = datetime.now()
