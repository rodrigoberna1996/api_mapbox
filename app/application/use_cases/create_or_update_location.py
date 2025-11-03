"""Use case for creating or updating a location aggregate."""
from __future__ import annotations

from app.application.dto.location import LocationCreate, LocationRead
from app.application.mappers.location_mapper import to_location_read
from app.domain.repositories.location_repository import LocationRepository


class CreateOrUpdateLocation:
    def __init__(self, repository: LocationRepository) -> None:
        self._repository = repository

    async def execute(self, payload: LocationCreate) -> LocationRead:
        clients_payload = [] if payload.es_global else [client.model_dump() for client in payload.clients]
        location = await self._repository.upsert_location(
            nombre_oficial=payload.nombre_oficial,
            codigo=payload.codigo,
            tipo=payload.tipo,
            activo=payload.activo,
            es_global=payload.es_global,
            address=payload.address.model_dump() if payload.address else None,
            aliases=[alias.alias for alias in payload.aliases],
            clients=clients_payload,
        )
        return to_location_read(location)
