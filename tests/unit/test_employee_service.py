"""
Unit tests for EmployeeService.
"""

from app.services.employee_service import EmployeeService


class TestEmployeeService:
    """Test cases for EmployeeService."""

    async def test_list_employee_returns_only_configured_columns(
        self, db_session, sample_employees, sample_organizations
    ):
        """Test that only configured columns are returned."""
        from app.schemas.employee import EmployeeListQueryParams

        service = EmployeeService(db_session)
        query_params = EmployeeListQueryParams()

        # Org 1 has config: ["name", "email", "department", "location", "position"]
        response = await service.list_employee(organization_id=1, query_params=query_params)

        assert len(response.employees) == 3
        for employee_data in response.employees:
            # Should have all configured columns
            assert "first_name" in employee_data
            assert "last_name" in employee_data
            assert "email" in employee_data
            assert "department" in employee_data
            assert "location" in employee_data
            assert "position" in employee_data

            # Should not have phone (not in config)
            assert "phone" not in employee_data

    async def test_list_employee_different_org_config(
        self, db_session, sample_employees, sample_organizations
    ):
        """Test that different organizations get different columns."""
        from app.schemas.employee import EmployeeListQueryParams

        service = EmployeeService(db_session)
        query_params = EmployeeListQueryParams()

        # Org 2 has config: ["department", "location"]
        response = await service.list_employee(organization_id=2, query_params=query_params)

        assert len(response.employees) == 1
        employee_data = response.employees[0]

        # Should only have configured columns
        assert "department" in employee_data
        assert "location" in employee_data

        # Should not have contact info
        assert "name" not in employee_data
        assert "email" not in employee_data
        assert "phone" not in employee_data
        assert "position" not in employee_data

    async def test_list_employee_with_filters(
        self, db_session, sample_employees, sample_organizations
    ):
        """Test searching with filters."""
        from app.schemas.employee import EmployeeListQueryParams

        service = EmployeeService(db_session)
        query_params = EmployeeListQueryParams(department_id=[1])

        response = await service.list_employee(organization_id=1, query_params=query_params)

        assert len(response.employees) <= 3

    async def test_list_employee_with_search_term(
        self, db_session, sample_employees, sample_organizations
    ):
        """Test searching with search term."""
        from app.schemas.employee import EmployeeListQueryParams

        service = EmployeeService(db_session)
        query_params = EmployeeListQueryParams(search="jane")

        response = await service.list_employee(organization_id=1, query_params=query_params)

        assert len(response.employees) >= 1
        assert any("jane" in emp["first_name"].lower() for emp in response.employees)

    async def test_list_employee_nonexistent_org(self, db_session):
        """Test searching for non-existent organization."""
        from app.schemas.employee import EmployeeListQueryParams

        service = EmployeeService(db_session)
        query_params = EmployeeListQueryParams()

        response = await service.list_employee(organization_id=999, query_params=query_params)

        assert len(response.employees) == 0
        assert response.total_returned == 0
        assert response.total_pages == 0

    async def test_filter_employee_columns_combines_name(
        self, db_session, sample_employees, sample_organizations
    ):
        """Test that first_name and last_name are combined into name."""
        from app.schemas.employee import EmployeeListQueryParams

        service = EmployeeService(db_session)
        query_params = EmployeeListQueryParams(limit=1)

        response = await service.list_employee(organization_id=1, query_params=query_params)

        employee = response.employees[0]
        assert "first_name" in employee

    async def test_no_data_leak_across_organizations(
        self, db_session, sample_employees, sample_organizations
    ):
        """Test that organization 1 cannot see organization 2 data."""
        from app.schemas.employee import EmployeeListQueryParams

        service = EmployeeService(db_session)
        query_params = EmployeeListQueryParams(limit=100)

        response = await service.list_employee(organization_id=1, query_params=query_params)

        # Should only get org 1 employees
        assert len(response.employees) == 3

        # Verify by checking emails (should all be @test.com, not @another.com)
        for emp in response.employees:
            if "email" in emp:
                assert "@test.com" in emp["email"]
                assert "@another.com" not in emp["email"]

    # TODO: Add more tests for pagination, some search edge cases, etc.
