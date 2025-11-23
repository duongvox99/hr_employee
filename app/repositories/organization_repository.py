from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization


class OrganizationRepository:
    """Repository for organization-related database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_organization(self, organization_id: int) -> Organization | None:
        """Get organization by ID."""
        query = select(Organization).filter(Organization.id == organization_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_display_columns(self, organization_id: int) -> list[str] | None:
        """
        Get the list of columns to display for an organization.
        Returns None if not exist organization, default columns if organization doesn't exist.
        """
        org = await self.get_organization(organization_id)
        if not org:
            return None

        if org.display_columns:
            return org.display_columns

        # Default columns if organization doesn't exist or no config
        return [
            "first_name",
            "last_name",
            "email",
            "phone",
            "department",
            "position",
            "location",
            "status",
        ]
