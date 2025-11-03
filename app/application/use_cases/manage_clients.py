"""Use cases for managing external client links."""
from __future__ import annotations

from datetime import datetime
from fastapi import HTTPException, status

from app.application.dto.location import ClientDeleteRequest, ClientRead, ClientRef
from app.domain.models.location import ClientLink
from app.domain.repositories.location_repository import LocationRepository


class AddClientLink:
    def __init__(self, repository: LocationRepository) -> None:
        self._repository = repository

    async def execute(self, location_id: int, payload: ClientRef) -> ClientRead:
        client = ClientLink(
            localidad_id=location_id,
            cliente_source=payload.cliente_source,
            cliente_external_id=payload.cliente_external_id,
            rol=payload.rol,
            created_at=datetime.utcnow(),
        )
        result = await self._repository.add_client(location_id, client)
        return ClientRead.model_validate(
            {
                "cliente_source": result.cliente_source,
                "cliente_external_id": result.cliente_external_id,
                "rol": result.rol,
                "created_at": result.created_at,
            }
        )


class RemoveClientLink:
    def __init__(self, repository: LocationRepository) -> None:
        self._repository = repository

    async def execute(self, location_id: int, payload: ClientDeleteRequest) -> None:
        try:
            await self._repository.remove_client(
                location_id,
                cliente_source=payload.cliente_source,
                cliente_external_id=payload.cliente_external_id,
                rol=payload.rol,
            )
        except ValueError as exc:
            raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
