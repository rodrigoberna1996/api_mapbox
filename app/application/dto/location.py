"""DTO definitions for location operations."""
from __future__ import annotations

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field, field_validator

from app.domain.models.location import LocationType


def _strip(value: str | None) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


class AddressDTO(BaseModel):
    calle: str | None = Field(None, max_length=255)
    colonia: str | None = Field(None, max_length=255)
    ciudad_text: str | None = Field(None, max_length=255)
    estado_text: str | None = Field(None, max_length=255)
    cp: str | None = Field(None, max_length=20)
    lat: float | None = Field(None, ge=-90.0, le=90.0)
    lng: float | None = Field(None, ge=-180.0, le=180.0)
    referencia: str | None = Field(None, max_length=500)

    _normalize = field_validator(
        "calle",
        "colonia",
        "ciudad_text",
        "estado_text",
        "cp",
        "referencia",
        mode="before",
    )(_strip)


class ClientRef(BaseModel):
    cliente_source: str = Field(..., min_length=1, max_length=50)
    cliente_external_id: str = Field(..., min_length=1, max_length=100)
    rol: str = Field(..., min_length=1, max_length=50)

    model_config = {
        "json_schema_extra": {
            "example": {
                "cliente_source": "erp",
                "cliente_external_id": "123",
                "rol": "Operador",
            }
        },
        "populate_by_name": True,
    }


class AliasDTO(BaseModel):
    alias: str = Field(..., min_length=1, max_length=255)

    _normalize = field_validator("alias", mode="before")(_strip)


class LocationBase(BaseModel):
    nombre_oficial: str = Field(..., min_length=1, max_length=255)
    codigo: str = Field(..., min_length=1, max_length=50)
    tipo: LocationType = LocationType.AMBOS
    activo: bool = True
    es_global: bool = False

    _normalize_nombre = field_validator("nombre_oficial", mode="before")(_strip)
    _normalize_codigo = field_validator("codigo", mode="before")(_strip)


class LocationCreate(LocationBase):
    address: AddressDTO | None = None
    aliases: list[AliasDTO] = Field(default_factory=list)
    clients: list[ClientRef] = Field(default_factory=list)


class LocationUpdate(BaseModel):
    nombre_oficial: str | None = Field(None, min_length=1, max_length=255)
    codigo: str | None = Field(None, min_length=1, max_length=50)
    tipo: LocationType | None = None
    activo: bool | None = None
    es_global: bool | None = None

    _normalize_nombre = field_validator("nombre_oficial", mode="before")(_strip)
    _normalize_codigo = field_validator("codigo", mode="before")(_strip)

    @field_validator("nombre_oficial", "codigo", mode="after")
    def _validate_nullable(cls, value: str | None) -> str | None:  # noqa: D417
        if value is not None and not value:
            raise ValueError("El valor no puede estar vacío")
        return value


class AddressUpdate(AddressDTO):
    pass


class AliasRead(BaseModel):
    id: int
    alias: str
    created_at: datetime


class ClientRead(BaseModel):
    cliente_source: str
    cliente_external_id: str
    rol: str
    created_at: datetime


class AddressRead(AddressDTO):
    created_at: datetime
    updated_at: datetime


class LocationRead(BaseModel):
    id: int
    nombre_oficial: str
    codigo: str
    tipo: LocationType
    activo: bool
    es_global: bool
    created_at: datetime
    updated_at: datetime
    address: AddressRead | None = None
    aliases: list[AliasRead] = Field(default_factory=list)
    clients: list[ClientRead] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 123,
                "nombre_oficial": "Terminal Norte",
                "codigo": "TN-001",
                "tipo": "Origen",
                "activo": True,
                "es_global": False,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "address": {
                    "calle": "Av. Central",
                    "colonia": "Centro",
                    "ciudad_text": "CDMX",
                    "estado_text": "Ciudad de México",
                    "cp": "06000",
                    "lat": 19.4326,
                    "lng": -99.1332,
                    "referencia": "Frente a la estación",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                },
                "aliases": [
                    {"id": "...", "alias": "Terminal Centro", "created_at": "..."}
                ],
                "clients": [
                    {
                        "cliente_source": "erp",
                        "cliente_external_id": "123",
                        "rol": "Operador",
                        "created_at": "2024-01-01T00:00:00Z",
                    }
                ],
            }
        }
    }


class LocationListResponse(BaseModel):
    items: list[LocationRead]
    total: int


class ClientDeleteRequest(BaseModel):
    cliente_source: str
    cliente_external_id: str
    rol: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "cliente_source": "erp",
                "cliente_external_id": "123",
                "rol": "Operador",
            }
        }
    }
