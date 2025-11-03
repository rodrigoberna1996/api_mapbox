"""Use case for retrieving paginated locations with filters."""
from __future__ import annotations

from app.application.dto.location import LocationListResponse, LocationRead
from app.application.mappers.location_mapper import to_location_read
from app.domain.repositories.location_repository import (
    LocationFilters,
    LocationRepository,
    Pagination,
)


class ListLocations:
    def __init__(self, repository: LocationRepository) -> None:
        self._repository = repository

    async def execute(
        self,
        filters: LocationFilters,
        pagination: Pagination,
    ) -> LocationListResponse:
        items, total = await self._repository.list_locations(filters, pagination)
        return LocationListResponse(
            items=[to_location_read(item) for item in items],
            total=total,
        )
