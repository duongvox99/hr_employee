"""
Unit tests for EmployeeRepository.
"""

from app.repositories.employee_repository import EmployeeRepository
from app.schemas.employee import EmployeeListQueryParams


class TestEmployeeRepository:
    """Test cases for EmployeeRepository."""

    async def test_list_employee_by_organization(self, db_session, sample_employees):
        """Test searching employees filtered by organization."""
        repo = EmployeeRepository(db_session)

        # Search in organization 1
        rows, total_count = await repo.list_employee(
            organization_id=1, query_params=EmployeeListQueryParams()
        )

        # Should return only org 1's employees
        assert len(rows) == 3
        employees = [row[0] for row in rows]
        assert all(e.organization_id == 1 for e in employees)
        assert total_count == 3

    async def test_list_employee_by_department(self, db_session, sample_employees):
        """Test searching employees filtered by department."""
        repo = EmployeeRepository(db_session)

        # Filter by single department (using list)
        rows, total_count = await repo.list_employee(
            organization_id=1, query_params=EmployeeListQueryParams(department_id=[1])
        )

        # Should return only org 1's employees and department 1
        assert len(rows) == 2
        employees = [row[0] for row in rows]
        assert all(e.organization_id == 1 for e in employees)
        assert total_count == 2

    async def test_list_employee_by_multiple_departments(self, db_session, sample_employees):
        """Test searching employees filtered by multiple departments."""
        repo = EmployeeRepository(db_session)

        # Filter by multiple departments
        rows, total_count = await repo.list_employee(
            organization_id=1, query_params=EmployeeListQueryParams(department_id=[1, 2])
        )

        # Should return only org 1's employees and department 1 & 2
        assert len(rows) == 3
        employees = [row[0] for row in rows]
        assert all(e.organization_id in [1, 2] for e in employees)
        assert total_count == 3

    async def test_list_employee_by_name(self, db_session, sample_employees):
        """Test searching employees by name."""
        repo = EmployeeRepository(db_session)

        rows, total_count = await repo.list_employee(
            organization_id=1, query_params=EmployeeListQueryParams(search="john")
        )

        # Should return employees with "john" in their name or email or phone
        employees = [row[0] for row in rows]
        assert len(employees) >= 1
        assert any("john" in (e.first_name + e.last_name).lower() for e in employees)
        assert total_count == 2

    # TODO: Add more tests for other filters like status, position, pagination, etc.
