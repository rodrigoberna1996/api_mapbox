"""Conversion utilities between domain entities and DTOs."""
from __future__ import annotations

from app.application.dto.location import (
    AddressRead,
    AliasRead,
    ClientRead,
    LocationRead,
)
from app.domain.models.location import Location


def to_location_read(location: Location) -> LocationRead:
    address = None
    if location.address is not None:
        address = AddressRead.model_validate(
            {
                "calle": location.address.calle,
                "colonia": location.address.colonia,
                "ciudad_text": location.address.ciudad_text,
                "estado_text": location.address.estado_text,
                "cp": location.address.cp,
                "lat": location.address.lat,
                "lng": location.address.lng,
                "referencia": location.address.referencia,
                "created_at": location.address.created_at,
                "updated_at": location.address.updated_at,
            }
        )

    aliases = [
        AliasRead.model_validate(
            {
                "id": alias.id,
                "alias": alias.alias,
                "created_at": alias.created_at,
            }
        )
        for alias in location.aliases
    ]

    clients = [
        ClientRead.model_validate(
            {
                "cliente_source": client.cliente_source,
                "cliente_external_id": client.cliente_external_id,
                "rol": client.rol,
                "created_at": client.created_at,
            }
        )
        for client in location.clients
    ]

    payload = {
        "id": location.id,
        "nombre_oficial": location.nombre_oficial,
        "codigo": location.codigo,
        "tipo": location.tipo,
        "activo": location.activo,
        "es_global": location.es_global,
        "created_at": location.created_at,
        "updated_at": location.updated_at,
        "address": address,
        "aliases": aliases,
        "clients": clients,
    }
    return LocationRead.model_validate(payload)
