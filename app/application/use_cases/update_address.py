"""Use case for updating or creating a location address."""
from __future__ import annotations

from fastapi import HTTPException, status

from app.application.dto.location import AddressUpdate, LocationRead
from app.application.mappers.location_mapper import to_location_read
from app.domain.repositories.location_repository import LocationRepository


class UpdateLocationAddress:
    def __init__(self, repository: LocationRepository) -> None:
        self._repository = repository

    async def execute(self, location_id: int, payload: AddressUpdate) -> LocationRead:
        updated = await self._repository.update_address(
            location_id,
            payload.model_dump(exclude_none=True),
        )
        if updated is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Localidad no encontrada")
        return to_location_read(updated)
