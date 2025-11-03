"""Use cases for managing location aliases."""
from __future__ import annotations

from fastapi import HTTPException, status

from app.application.dto.location import AliasDTO, AliasRead
from app.domain.repositories.location_repository import LocationRepository


class AddLocationAlias:
    def __init__(self, repository: LocationRepository) -> None:
        self._repository = repository

    async def execute(self, location_id: int, payload: AliasDTO) -> AliasRead:
        alias = await self._repository.add_alias(location_id, payload.alias)
        return AliasRead.model_validate(
            {
                "id": alias.id,
                "alias": alias.alias,
                "created_at": alias.created_at,
            }
        )


class RemoveLocationAlias:
    def __init__(self, repository: LocationRepository) -> None:
        self._repository = repository

    async def execute(self, location_id: int, alias_id: int) -> None:
        try:
            await self._repository.remove_alias(location_id, alias_id)
        except ValueError as exc:  # repository signals missing records
            raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
