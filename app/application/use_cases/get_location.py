"""Use case for retrieving a single location aggregate."""
from __future__ import annotations

from fastapi import HTTPException, status

from app.application.dto.location import LocationRead
from app.application.mappers.location_mapper import to_location_read
from app.domain.repositories.location_repository import LocationRepository


class GetLocation:
    def __init__(self, repository: LocationRepository) -> None:
        self._repository = repository

    async def execute(self, location_id: int) -> LocationRead:
        location = await self._repository.get_location(location_id)
        if location is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Localidad no encontrada")
        return to_location_read(location)
