from typing import Any

from pydantic import BaseModel, Field

from app.models import EmployeeStatus


class EmployeeListQueryParams(BaseModel):
    """Query parameters for employee list endpoint."""

    search: str | None = Field(
        None, description="Search term for name, email, or phone", max_length=100
    )
    status: EmployeeStatus | None = Field(
        None, description="Filter by employee status (Active, Not Started, Terminated)"
    )
    location_id: list[int] | None = Field(
        None, description="Filter by location IDs (supports multiple)"
    )
    company_id: list[int] | None = Field(
        None, description="Filter by company IDs (supports multiple)"
    )
    department_id: list[int] | None = Field(
        None, description="Filter by department IDs (supports multiple)"
    )
    position_id: list[int] | None = Field(
        None, description="Filter by position IDs (supports multiple)"
    )
    limit: int = Field(50, description="Number of results per page", ge=1, le=100)
    page: int = Field(
        1, description="Page number (1-indexed)", ge=1
    )


class EmployeeListResponse(BaseModel):
    """Response model for list employee."""

    display_columns: list[str] | None = Field(..., description="List of configured columns")
    employees: list[dict[str, Any]] = Field(
        ..., description="List of employees with configured columns"
    )
    total_returned: int = Field(..., description="Number of employees in current response")
    total_records: int = Field(..., description="Total number of records matching the filters")
    total_pages: int = Field(..., description="Total number of pages")
    page: int = Field(..., description="Current page number")
