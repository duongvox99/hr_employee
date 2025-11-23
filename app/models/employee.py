import enum

from sqlalchemy import Column, ForeignKey, Integer, String

from app.models.base import Base


class EmployeeStatus(enum.Enum):
    """Employee status enum"""

    ACTIVE = "Active"
    NOT_STARTED = "Not Started"
    TERMINATED = "Terminated"


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)

    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50))
    avatar = Column(String(500))  # URL to avatar image

    # Work Information - Foreign keys to related tables
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True, index=True)
    position_id = Column(Integer, ForeignKey("positions.id"), nullable=True, index=True)
    status = Column(String(20), nullable=False, default=EmployeeStatus.NOT_STARTED.value)
