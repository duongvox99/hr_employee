import math
from typing import Any

from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.employee_repository import EmployeeRepository
from app.repositories.organization_repository import OrganizationRepository
from app.schemas.employee import EmployeeListQueryParams, EmployeeListResponse
from app.utils.pagination_cache import pagination_cache


class EmployeeService:
    """Service layer for employee operations with business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.employee_repo = EmployeeRepository(db)
        self.org_repo = OrganizationRepository(db)

    async def list_employee(
        self,
        organization_id: int,
        query_params: EmployeeListQueryParams,
    ) -> EmployeeListResponse:
        """
        Search employees with filters and return only configured columns.
        Supports both page-based and cursor-based pagination.
        """
        # Get configured columns for this organization
        display_columns = await self.org_repo.get_display_columns(organization_id=organization_id)
        if display_columns is None:
            # Organization does not exist, return empty response
            return EmployeeListResponse(
                display_columns=None,
                employees=[],
                total_returned=0,
                total_records=0,
                total_pages=0,
                page=1,
            )

        pagination_cache_key = pagination_cache.generate_cache_key(
            organization_id=organization_id,
            search=query_params.search,
            department_id=query_params.department_id,
            location_id=query_params.location_id,
            position_id=query_params.position_id,
            status=query_params.status,
            limit=query_params.limit,
        )

        endpoint = "list_employee"
        page = query_params.page
        rows, total_count = await self.employee_repo.list_employee(
            organization_id=organization_id,
            query_params=query_params,
            previous_id=pagination_cache.get_cursor(
                endpoint=endpoint, cache_key=pagination_cache_key, page=page
            ),
        )

        if len(rows):
            # Cache the current page cursor for effective page-based pagination by leveraging keyset pagination
            pagination_cache.set_cursor(
                endpoint=endpoint,
                cache_key=pagination_cache_key,
                page=page,
                previous_id=rows[0][0].id - 1,  # first employee id in the current page - 1
            )

            # Cache the next page cursor for effective page-based pagination by leveraging keyset pagination
            pagination_cache.set_cursor(
                endpoint=endpoint,
                cache_key=pagination_cache_key,
                page=page + 1,
                previous_id=rows[-1][0].id,  # last employee id in the current page
            )

        employee_data = [
            self._filter_employee_columns_from_joined_data(row=row, display_columns=display_columns)
            for row in rows
        ]
        return EmployeeListResponse(
            display_columns=display_columns,
            employees=employee_data,
            total_returned=len(employee_data),
            total_records=total_count,
            total_pages=math.ceil(total_count / query_params.limit) if total_count > 0 else 0,
            page=page,
        )

    @staticmethod
    def _filter_employee_columns_from_joined_data(
        row: Row,
        display_columns: list[str],
    ) -> dict[str, Any]:
        """
        Filter employee data to include only configured columns.
        """
        employee, department_name, position_name, location_name = row

        # Mapping of display column names to employee attributes
        column_mapping = {
            "avatar": lambda e: e.avatar,
            "first_name": lambda e: e.first_name,
            "last_name": lambda e: e.last_name,
            "email": lambda e: e.email,
            "phone": lambda e: e.phone,
            "department": lambda e: department_name,
            "position": lambda e: position_name,
            "location": lambda e: location_name,
            "status": lambda e: e.status,
        }

        result = {"id": employee.id}  # Always include ID

        # Build result with only configured columns
        for column in display_columns:
            if column in column_mapping:
                value = column_mapping[column](employee)
                result[column] = value

        return result
