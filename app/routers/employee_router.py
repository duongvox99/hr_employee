from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.decorators.rate_limit import rate_limit
from app.models.user import User
from app.schemas.employee import EmployeeListQueryParams, EmployeeListResponse
from app.services.employee_service import EmployeeService

router = APIRouter(prefix="/api/v1/employees", tags=["Employees"])


@router.get("")
@rate_limit(max_requests=2, window_seconds=60)
async def list_employee(
    query_params: Annotated[EmployeeListQueryParams, Query()],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EmployeeListResponse:
    """
    List employees with filters and pagination.
    Rate limited to 2 requests per minute per user.
    """
    service = EmployeeService(db)
    return await service.list_employee(
        organization_id=current_user.organization_id,
        query_params=query_params,
    )
