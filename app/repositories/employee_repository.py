from sqlalchemy import Row, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.department import Department
from app.models.employee import Employee
from app.models.location import Location
from app.models.position import Position
from app.schemas.employee import EmployeeListQueryParams


class EmployeeRepository:
    """Repository for employee-related database operations with id-based pagination."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_employee(
        self,
        organization_id: int,
        query_params: EmployeeListQueryParams,
        previous_id: int | None = None,
    ) -> tuple[list[Row[tuple[Employee, str, str, str]]], int]:
        """
        Search employees with filters using id-based keyset pagination.
        Uses JOINs to fetch related department, location, and position names.

        Args:
            organization_id: Organization ID to filter by
            query_params: EmployeeListQueryParams object for filtering
            previous_id: last employee ID from previous page for key set pagination

        Returns:
            Tuple of (employee data list with joined names, total_count)
            Each item in list is (Employee, department_name, location_name, position_name)
        """
        # Count total records with same filters (for pagination metadata)
        count_query = select(func.count(Employee.id)).filter(
            Employee.organization_id == organization_id
        )

        # Start with base query filtered by organization with JOINs
        query = (
            select(
                Employee,
                Department.name.label("department_name"),
                Location.name.label("location_name"),
                Position.name.label("position_name"),
            )
            .outerjoin(Department, Employee.department_id == Department.id)
            .outerjoin(Location, Employee.location_id == Location.id)
            .outerjoin(Position, Employee.position_id == Position.id)
            .filter(Employee.organization_id == organization_id)
        )

        # Apply search filter
        if query_params.search:
            search_term = f"%{query_params.search}%"
            search_filter = or_(
                Employee.first_name.ilike(search_term),
                Employee.last_name.ilike(search_term),
                Employee.email.ilike(search_term),
                Employee.phone.ilike(search_term),
            )
            query = query.filter(search_filter)
            count_query = count_query.filter(search_filter)

        # Apply company filter (supports multiple IDs)
        if query_params.company_id and len(query_params.company_id) > 0:
            company_filter = Employee.company_id.in_(query_params.company_id)
            query = query.filter(company_filter)
            count_query = count_query.filter(company_filter)

        # Apply department filter (supports multiple IDs)
        if query_params.department_id and len(query_params.department_id) > 0:
            dept_filter = Employee.department_id.in_(query_params.department_id)
            query = query.filter(dept_filter)
            count_query = count_query.filter(dept_filter)

        # Apply location filter (supports multiple IDs)
        if query_params.location_id and len(query_params.location_id) > 0:
            loc_filter = Employee.location_id.in_(query_params.location_id)
            query = query.filter(loc_filter)
            count_query = count_query.filter(loc_filter)

        # Apply position filter (supports multiple IDs)
        if query_params.position_id and len(query_params.position_id) > 0:
            pos_filter = Employee.position_id.in_(query_params.position_id)
            query = query.filter(pos_filter)
            count_query = count_query.filter(pos_filter)

        # Apply status filter
        if query_params.status:
            status_filter = Employee.status == query_params.status.value
            query = query.filter(status_filter)
            count_query = count_query.filter(status_filter)

        # Get total count
        count_result = await self.db.execute(count_query)
        total_count = count_result.scalar() or 0

        if previous_id:
            # Apply id-based keyset pagination if previous_id is provided
            query = query.filter(Employee.id > previous_id)
        elif query_params.page > 1:
            # Apply offset-based pagination as fallback
            query = query.offset((query_params.page - 1) * query_params.limit)

        # Order by id for consistent pagination
        query = query.order_by(Employee.id.asc())

        query = query.limit(query_params.limit)
        result = await self.db.execute(query)
        rows = list(result.all())

        return rows, total_count
