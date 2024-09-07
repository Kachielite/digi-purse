from sqlalchemy import Column, ForeignKey, Float, Enum, DateTime, String, event
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from datetime import datetime
import uuid

from app.db.base import Base


class Transaction(Base):
    __tablename__ = "transaction"

    id = Column(pgUUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    wallet_id = Column(pgUUID(as_uuid=True), ForeignKey("wallet.id"), index=True, nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(Enum("credit", "balance", "debit", "refund", name="transaction_type"), nullable=False)
    description = Column(String, nullable=True)
    source = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


@event.listens_for(Transaction, "before_update")
def receive_before_update(mapper, connection, target):
    target.updated_at = datetime.now()
