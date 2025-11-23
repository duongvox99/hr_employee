from sqlalchemy import JSON, Column, Integer, String

from app.models.base import Base


class Organization(Base):
    """
    Organization model with display column configuration.
    The columns field is a JSON array defining the column order and visibility (already discussed & agreed with FE).
    Example: ["first_name", "last_name", "email", "phone", "department", "location", "position"]
    """

    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    display_columns = Column(JSON, nullable=False)  # List of column names in display order
