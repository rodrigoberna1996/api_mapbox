"""Use case for deleting a location."""
from __future__ import annotations

from fastapi import HTTPException, status

from app.domain.repositories.location_repository import LocationRepository


class DeleteLocation:
    def __init__(self, repository: LocationRepository) -> None:
        self._repository = repository

    async def execute(self, location_id: int) -> None:
        deleted = await self._repository.delete_location(location_id)
        if not deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Localidad no encontrada")
