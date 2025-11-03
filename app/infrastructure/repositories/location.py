"""SQLAlchemy implementation for location repository."""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models.location import Address, Alias, ClientLink, Location, LocationType
from app.domain.repositories.location_repository import (
    LocationFilters,
    LocationRepository,
    Pagination,
)
from app.infrastructure.db.models import (
    AddressModel,
    LocationAliasModel,
    LocationClientModel,
    LocationModel,
)


class SQLAlchemyLocationRepository(LocationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert_location(
        self,
        *,
        nombre_oficial: str,
        codigo: str,
        tipo: LocationType,
        activo: bool,
        es_global: bool,
        address: dict | None,
        aliases: Sequence[str],
        clients: Sequence[dict],
    ) -> Location:
        location = await self._get_model_by_codigo(codigo)
        if location is None:
            location = LocationModel(
                nombre_oficial=nombre_oficial,
                codigo=codigo,
                tipo=tipo,
                activo=activo,
                es_global=es_global,
            )
            self._session.add(location)
            await self._session.flush()
        else:
            location.nombre_oficial = nombre_oficial
            location.tipo = tipo
            location.activo = activo
            location.es_global = es_global

        if address:
            await self._apply_address(location, address)
        if aliases is not None:
            await self._apply_aliases(location, aliases)
        if clients is not None:
            await self._apply_clients(location, clients)

        await self._session.commit()
        refreshed = await self._get_model(location.id)
        if refreshed is None:
            raise RuntimeError("Location not found after upsert")
        return self._to_domain(refreshed)

    async def list_locations(
        self, filters: LocationFilters, pagination: Pagination
    ) -> tuple[list[Location], int]:
        data_stmt = self._apply_filters(self._base_query(), filters)
        data_stmt = data_stmt.order_by(LocationModel.nombre_oficial).limit(pagination.limit).offset(
            pagination.offset
        )

        count_stmt = self._apply_filters(
            select(func.count(func.distinct(LocationModel.id))).select_from(LocationModel),
            filters,
        )

        result = await self._session.execute(data_stmt)
        rows = result.scalars().unique().all()
        total = (await self._session.execute(count_stmt)).scalar_one()
        return [self._to_domain(row) for row in rows], total

    async def get_location(self, location_id: int) -> Location | None:
        stmt = self._base_query().where(LocationModel.id == location_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def update_location(
        self,
        location_id: int,
        *,
        nombre_oficial: str | None,
        codigo: str | None,
        tipo: LocationType | None,
        activo: bool | None,
        es_global: bool | None,
    ) -> Location | None:
        model = await self._get_model(location_id)
        if model is None:
            return None
        if nombre_oficial is not None:
            model.nombre_oficial = nombre_oficial
        if codigo is not None:
            model.codigo = codigo
        if tipo is not None:
            model.tipo = tipo
        if activo is not None:
            model.activo = activo
        if es_global is not None:
            model.es_global = es_global

        await self._session.commit()
        refreshed = await self._get_model(model.id)
        if refreshed is None:
            return None
        return self._to_domain(refreshed)

    async def update_address(self, location_id: int, data: dict) -> Location | None:
        model = await self._get_model(location_id)
        if model is None:
            return None
        await self._apply_address(model, data)
        await self._session.commit()
        refreshed = await self._get_model(model.id)
        if refreshed is None:
            return None
        return self._to_domain(refreshed)

    async def add_alias(self, location_id: int, alias: str) -> Alias:
        model = await self._get_model(location_id)
        if model is None:
            raise ValueError("Localidad no encontrada")
        existing = next((item for item in model.aliases if item.alias == alias), None)
        if existing is None:
            alias_model = LocationAliasModel(localidad_id=model.id, alias=alias)
            self._session.add(alias_model)
            await self._session.flush()
            await self._session.refresh(alias_model)
        else:
            alias_model = existing
        await self._session.commit()
        return self._alias_to_domain(alias_model)

    async def remove_alias(self, location_id: int, alias_id: int) -> None:
        stmt = select(LocationAliasModel).where(
            LocationAliasModel.id == alias_id,
            LocationAliasModel.localidad_id == location_id,
        )
        result = await self._session.execute(stmt)
        alias = result.scalar_one_or_none()
        if alias is None:
            raise ValueError("Alias no encontrado")
        await self._session.delete(alias)
        await self._session.commit()

    async def add_client(self, location_id: int, client: ClientLink) -> ClientLink:
        model = await self._get_model(location_id)
        if model is None:
            raise ValueError("Localidad no encontrada")
        stmt = select(LocationClientModel).where(
            LocationClientModel.localidad_id == model.id,
            LocationClientModel.cliente_source == client.cliente_source,
            LocationClientModel.cliente_external_id == client.cliente_external_id,
            LocationClientModel.rol == client.rol,
        )
        result = await self._session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing is None:
            client_model = LocationClientModel(
                localidad_id=model.id,
                cliente_source=client.cliente_source,
                cliente_external_id=client.cliente_external_id,
                rol=client.rol,
            )
            self._session.add(client_model)
            await self._session.flush()
            await self._session.refresh(client_model)
        else:
            client_model = existing
        await self._session.commit()
        return self._client_to_domain(client_model)

    async def remove_client(
        self,
        location_id: int,
        *,
        cliente_source: str,
        cliente_external_id: str,
        rol: str,
    ) -> None:
        stmt = select(LocationClientModel).where(
            LocationClientModel.localidad_id == location_id,
            LocationClientModel.cliente_source == cliente_source,
            LocationClientModel.cliente_external_id == cliente_external_id,
            LocationClientModel.rol == rol,
        )
        result = await self._session.execute(stmt)
        client = result.scalar_one_or_none()
        if client is None:
            raise ValueError("Cliente no encontrado")
        await self._session.delete(client)
        await self._session.commit()

    async def _get_model_by_codigo(self, codigo: str) -> LocationModel | None:
        stmt = self._base_query().where(LocationModel.codigo == codigo)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_model(self, location_id: int) -> LocationModel | None:
        stmt = self._base_query().where(LocationModel.id == location_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    def _base_query(self) -> Select[LocationModel]:
        return select(LocationModel).options(
            selectinload(LocationModel.address),
            selectinload(LocationModel.aliases),
            selectinload(LocationModel.clients),
        )

    def _apply_filters(self, stmt: Select[Any], filters: LocationFilters) -> Select[Any]:
        if filters.query:
            pattern = f"%{filters.query}%"
            stmt = stmt.where(
                (LocationModel.nombre_oficial.ilike(pattern))
                | (LocationModel.codigo.ilike(pattern))
            )
        if filters.tipo:
            stmt = stmt.where(LocationModel.tipo == filters.tipo)
        if filters.activo is not None:
            stmt = stmt.where(LocationModel.activo == filters.activo)
        if any([filters.estado, filters.ciudad]):
            stmt = stmt.join(LocationModel.address, isouter=True)
            if filters.estado:
                stmt = stmt.where(AddressModel.estado_text.ilike(f"%{filters.estado}%"))
            if filters.ciudad:
                stmt = stmt.where(AddressModel.ciudad_text.ilike(f"%{filters.ciudad}%"))
        if filters.cliente_source or filters.cliente_external_id:
            stmt = stmt.join(LocationModel.clients, isouter=True)
            conditions = []
            if filters.cliente_source:
                conditions.append(
                    LocationClientModel.cliente_source == filters.cliente_source
                )
            if filters.cliente_external_id:
                conditions.append(
                    LocationClientModel.cliente_external_id == filters.cliente_external_id
                )
            match_condition = and_(*conditions) if conditions else None
            if match_condition is not None:
                stmt = stmt.where(
                    or_(
                        LocationModel.es_global.is_(True),
                        match_condition,
                    )
                )
            else:
                stmt = stmt.where(LocationModel.es_global.is_(True))
        return stmt

    async def _apply_address(self, model: LocationModel, data: dict) -> None:
        stmt = select(AddressModel).where(AddressModel.localidad_id == model.id)
        result = await self._session.execute(stmt)
        address_model = result.scalar_one_or_none()

        if address_model is None:
            address_model = AddressModel(localidad_id=model.id, **data)
            self._session.add(address_model)
        else:
            for key, value in data.items():
                setattr(address_model, key, value)

        model.address = address_model
        await self._session.flush()

    async def _apply_aliases(self, model: LocationModel, aliases: Sequence[str]) -> None:
        stmt = select(LocationAliasModel).where(LocationAliasModel.localidad_id == model.id)
        result = await self._session.execute(stmt)
        aliases_models = result.scalars().all()
        existing_aliases = {alias.alias: alias for alias in aliases_models}
        target_aliases = {alias for alias in aliases if alias}

        # remove aliases not present anymore
        for alias_value, alias_model in list(existing_aliases.items()):
            if alias_value not in target_aliases:
                await self._session.delete(alias_model)

        # add new aliases
        for alias_value in target_aliases:
            if alias_value not in existing_aliases:
                self._session.add(
                    LocationAliasModel(localidad_id=model.id, alias=alias_value)
                )
        await self._session.flush()

    async def _apply_clients(self, model: LocationModel, clients: Sequence[dict]) -> None:
        stmt = select(LocationClientModel).where(
            LocationClientModel.localidad_id == model.id
        )
        result = await self._session.execute(stmt)
        client_models = result.scalars().all()
        existing = {
            (client.cliente_source, client.cliente_external_id, client.rol): client
            for client in client_models
        }
        target = {
            (
                item["cliente_source"],
                item["cliente_external_id"],
                item["rol"],
            )
            for item in clients
        }

        for key, client_model in list(existing.items()):
            if key not in target:
                await self._session.delete(client_model)

        for item in clients:
            key = (
                item["cliente_source"],
                item["cliente_external_id"],
                item["rol"],
            )
            if key not in existing:
                self._session.add(LocationClientModel(localidad_id=model.id, **item))
        await self._session.flush()

    def _to_domain(self, model: LocationModel) -> Location:
        address = (
            Address(
                localidad_id=model.address.localidad_id,
                calle=model.address.calle,
                colonia=model.address.colonia,
                ciudad_text=model.address.ciudad_text,
                estado_text=model.address.estado_text,
                cp=model.address.cp,
                lat=model.address.lat,
                lng=model.address.lng,
                referencia=model.address.referencia,
                created_at=model.address.created_at,
                updated_at=model.address.updated_at,
            )
            if model.address
            else None
        )
        aliases = [self._alias_to_domain(alias) for alias in model.aliases]
        clients = [self._client_to_domain(client) for client in model.clients]
        return Location(
            id=model.id,
            nombre_oficial=model.nombre_oficial,
            codigo=model.codigo,
            tipo=model.tipo,
            activo=model.activo,
            es_global=model.es_global,
            created_at=model.created_at,
            updated_at=model.updated_at,
            address=address,
            aliases=aliases,
            clients=clients,
        )

    def _alias_to_domain(self, model: LocationAliasModel) -> Alias:
        return Alias(
            id=model.id,
            localidad_id=model.localidad_id,
            alias=model.alias,
            created_at=model.created_at,
        )

    def _client_to_domain(self, model: LocationClientModel) -> ClientLink:
        return ClientLink(
            localidad_id=model.localidad_id,
            cliente_source=model.cliente_source,
            cliente_external_id=model.cliente_external_id,
            rol=model.rol,
            created_at=model.created_at,
        )
