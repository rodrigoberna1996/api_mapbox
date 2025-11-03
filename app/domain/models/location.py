"""Domain entities for the Location bounded context."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
class LocationType(StrEnum):
    ORIGEN = "Origen"
    DESTINO = "Destino"
    AMBOS = "Ambos"


@dataclass(slots=True, frozen=True)
class Address:
    localidad_id: int
    calle: str | None
    colonia: str | None
    ciudad_text: str | None
    estado_text: str | None
    cp: str | None
    lat: float | None
    lng: float | None
    referencia: str | None
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True, frozen=True)
class Alias:
    id: int
    localidad_id: int
    alias: str
    created_at: datetime


@dataclass(slots=True, frozen=True)
class ClientLink:
    localidad_id: int
    cliente_source: str
    cliente_external_id: str
    rol: str
    created_at: datetime


@dataclass(slots=True)
class Location:
    id: int
    nombre_oficial: str
    codigo: str
    tipo: LocationType = LocationType.AMBOS
    activo: bool = True
    es_global: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    address: Address | None = None
    aliases: list[Alias] = field(default_factory=list)
    clients: list[ClientLink] = field(default_factory=list)

    @classmethod
    def new(
        cls,
        nombre_oficial: str,
        codigo: str,
        tipo: LocationType = LocationType.AMBOS,
        activo: bool = True,
        es_global: bool = False,
        *,  # noqa: D417
        location_id: int,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> "Location":
        now = datetime.utcnow()
        return cls(
            id=location_id,
            nombre_oficial=nombre_oficial,
            codigo=codigo,
            tipo=tipo,
            activo=activo,
            es_global=es_global,
            created_at=created_at or now,
            updated_at=updated_at or now,
        )
