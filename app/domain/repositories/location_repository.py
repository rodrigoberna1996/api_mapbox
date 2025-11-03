"""Repository contract for persisting locations and related aggregates."""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from app.domain.models.location import Address, Alias, ClientLink, Location, LocationType


@dataclass(slots=True)
class LocationFilters:
    query: str | None = None
    cliente_source: str | None = None
    cliente_external_id: str | None = None
    estado: str | None = None
    ciudad: str | None = None
    tipo: LocationType | None = None
    activo: bool | None = None


@dataclass(slots=True)
class Pagination:
    limit: int = 50
    offset: int = 0


class LocationRepository(ABC):
    @abstractmethod
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
        """Create a new location or update the aggregate when the unique code already exists."""

    @abstractmethod
    async def list_locations(
        self, filters: LocationFilters, pagination: Pagination
    ) -> tuple[list[Location], int]:
        """Return the list of locations and the total count matching the filters."""

    @abstractmethod
    async def get_location(self, location_id: int) -> Location | None:
        """Return a location aggregate by identifier."""

    @abstractmethod
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
        """Update base fields and return the refreshed aggregate."""

    @abstractmethod
    async def update_address(self, location_id: int, data: dict) -> Location | None:
        """Replace or create the address for the location and return the aggregate."""

    @abstractmethod
    async def add_alias(self, location_id: int, alias: str) -> Alias:
        """Add a new alias to the location."""

    @abstractmethod
    async def remove_alias(self, location_id: int, alias_id: int) -> None:
        """Remove the alias from the location."""

    @abstractmethod
    async def add_client(self, location_id: int, client: ClientLink) -> ClientLink:
        """Attach an external client reference to the location."""

    @abstractmethod
    async def remove_client(
        self,
        location_id: int,
        *,
        cliente_source: str,
        cliente_external_id: str,
        rol: str,
    ) -> None:
        """Detach a client reference from the location."""
