from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func

from app.database import Base as SQLAlchemyBase


class Base(SQLAlchemyBase):
    """
    Base model class that includes common timestamp fields for all models.
    All models should inherit from this class and define their own 'id' field.
    """

    __abstract__ = True

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
