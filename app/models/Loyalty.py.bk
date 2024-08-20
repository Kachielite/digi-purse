from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, DateTime, event

from app.db.base import Base


class Loyalty(Base):
    __tablename__ = "loyalty"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), index=True)
    points = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


@event.listens_for(Loyalty, "before_update")
def receive_before_update(mapper, connection, target):
    target.updated_at = datetime.now()
