"""Use case for updating base fields of a location."""
from __future__ import annotations

from fastapi import HTTPException, status

from app.application.dto.location import LocationRead, LocationUpdate
from app.application.mappers.location_mapper import to_location_read
from app.domain.repositories.location_repository import LocationRepository


class UpdateLocation:
    def __init__(self, repository: LocationRepository) -> None:
        self._repository = repository

    async def execute(self, location_id: int, payload: LocationUpdate) -> LocationRead:
        updated = await self._repository.update_location(
            location_id,
            nombre_oficial=payload.nombre_oficial,
            codigo=payload.codigo,
            tipo=payload.tipo,
            activo=payload.activo,
            es_global=payload.es_global,
        )
        if updated is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Localidad no encontrada")
        return to_location_read(updated)
