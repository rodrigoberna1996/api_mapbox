"""API routes for locations management."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.location import (
    AddressUpdate,
    AliasDTO,
    AliasRead,
    ClientDeleteRequest,
    ClientRead,
    ClientRef,
    LocationCreate,
    LocationListResponse,
    LocationRead,
    LocationUpdate,
)
from app.application.use_cases.create_or_update_location import CreateOrUpdateLocation
from app.application.use_cases.get_location import GetLocation
from app.application.use_cases.list_locations import ListLocations
from app.application.use_cases.manage_aliases import AddLocationAlias, RemoveLocationAlias
from app.application.use_cases.manage_clients import AddClientLink, RemoveClientLink
from app.application.use_cases.delete_location import DeleteLocation
from app.application.use_cases.update_address import UpdateLocationAddress
from app.application.use_cases.update_location import UpdateLocation
from app.domain.models.location import LocationType
from app.domain.repositories.location_repository import LocationFilters, Pagination
from app.infrastructure.db.session import get_session
from app.infrastructure.repositories.location import SQLAlchemyLocationRepository

router = APIRouter(prefix="/locations", tags=["localidades"])


def _get_repository(session: AsyncSession) -> SQLAlchemyLocationRepository:
    return SQLAlchemyLocationRepository(session)


@router.post("", response_model=LocationRead, status_code=status.HTTP_201_CREATED)
async def create_or_update_location(
    payload: LocationCreate,
    session: AsyncSession = Depends(get_session),
) -> LocationRead:
    repository = _get_repository(session)
    use_case = CreateOrUpdateLocation(repository)
    return await use_case.execute(payload)


@router.get("", response_model=LocationListResponse)
async def list_locations(
    q: Annotated[str | None, Query(max_length=255)] = None,
    cliente_source: Annotated[str | None, Query(max_length=50)] = None,
    cliente_external_id: Annotated[str | None, Query(max_length=100)] = None,
    estado: Annotated[str | None, Query(max_length=255)] = None,
    ciudad: Annotated[str | None, Query(max_length=255)] = None,
    tipo: LocationType | None = Query(None),
    activo: bool | None = Query(None),
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    session: AsyncSession = Depends(get_session),
) -> LocationListResponse:
    filters = LocationFilters(
        query=q,
        cliente_source=cliente_source,
        cliente_external_id=cliente_external_id,
        estado=estado,
        ciudad=ciudad,
        tipo=tipo,
        activo=activo,
    )
    pagination = Pagination(limit=limit, offset=offset)
    repository = _get_repository(session)
    use_case = ListLocations(repository)
    return await use_case.execute(filters, pagination)


@router.get("/{location_id}", response_model=LocationRead)
async def get_location(
    location_id: int,
    session: AsyncSession = Depends(get_session),
) -> LocationRead:
    repository = _get_repository(session)
    use_case = GetLocation(repository)
    return await use_case.execute(location_id)


@router.put("/{location_id}", response_model=LocationRead)
async def update_location(
    location_id: int,
    payload: LocationUpdate,
    session: AsyncSession = Depends(get_session),
) -> LocationRead:
    if not payload.model_dump(exclude_none=True):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No hay campos para actualizar")
    repository = _get_repository(session)
    use_case = UpdateLocation(repository)
    return await use_case.execute(location_id, payload)


@router.put("/{location_id}/address", response_model=LocationRead)
async def update_location_address(
    location_id: int,
    payload: AddressUpdate,
    session: AsyncSession = Depends(get_session),
) -> LocationRead:
    repository = _get_repository(session)
    use_case = UpdateLocationAddress(repository)
    return await use_case.execute(location_id, payload)


@router.post("/{location_id}/aliases", response_model=AliasRead, status_code=status.HTTP_201_CREATED)
async def add_alias(
    location_id: int,
    payload: AliasDTO,
    session: AsyncSession = Depends(get_session),
) -> AliasRead:
    repository = _get_repository(session)
    use_case = AddLocationAlias(repository)
    alias = await use_case.execute(location_id, payload)
    return alias


@router.delete(
    "/{location_id}/aliases/{alias_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    response_model=None,
)
async def delete_alias(
    location_id: int,
    alias_id: int,
    session: AsyncSession = Depends(get_session),
) -> None:
    repository = _get_repository(session)
    use_case = RemoveLocationAlias(repository)
    await use_case.execute(location_id, alias_id)


@router.delete(
    "/{location_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    response_model=None,
)
async def delete_location(
    location_id: int,
    session: AsyncSession = Depends(get_session),
) -> None:
    repository = _get_repository(session)
    use_case = DeleteLocation(repository)
    await use_case.execute(location_id)


@router.post(
    "/{location_id}/clients",
    response_model=ClientRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_client(
    location_id: int,
    payload: ClientRef,
    session: AsyncSession = Depends(get_session),
) -> ClientRead:
    repository = _get_repository(session)
    use_case = AddClientLink(repository)
    return await use_case.execute(location_id, payload)


@router.delete(
    "/{location_id}/clients",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    response_model=None,
)
async def delete_client(
    location_id: int,
    payload: Annotated[ClientDeleteRequest, Body()],
    session: AsyncSession = Depends(get_session),
) -> None:
    repository = _get_repository(session)
    use_case = RemoveClientLink(repository)
    await use_case.execute(location_id, payload)


@router.get(
    "/by-client/{cliente_source}/{cliente_external_id}",
    response_model=LocationListResponse,
)
async def list_locations_by_client(
    cliente_source: str,
    cliente_external_id: str,
    q: Annotated[str | None, Query(max_length=255)] = None,
    estado: Annotated[str | None, Query(max_length=255)] = None,
    ciudad: Annotated[str | None, Query(max_length=255)] = None,
    tipo: LocationType | None = Query(None),
    activo: bool | None = Query(None),
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    session: AsyncSession = Depends(get_session),
) -> LocationListResponse:
    filters = LocationFilters(
        query=q,
        cliente_source=cliente_source,
        cliente_external_id=cliente_external_id,
        estado=estado,
        ciudad=ciudad,
        tipo=tipo,
        activo=activo,
    )
    pagination = Pagination(limit=limit, offset=offset)
    repository = _get_repository(session)
    use_case = ListLocations(repository)
    return await use_case.execute(filters, pagination)
