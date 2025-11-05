from __future__ import annotations

import pytest

from app.domain.models.location import LocationType


@pytest.mark.asyncio
async def test_create_location_upsert(client):
    payload = {
        "nombre_oficial": "Central Norte",
        "codigo": "LOC-001",
        "tipo": LocationType.ORIGEN.value,
        "activo": True,
        "es_global": False,
        "address": {
            "calle": "Av Principal",
            "colonia": "Centro",
            "ciudad_text": "CDMX",
            "estado_text": "Ciudad de México",
            "cp": "06000",
            "lat": 19.4326,
            "lng": -99.1332,
        },
        "aliases": [
            {"alias": "Terminal Centro"},
        ],
        "clients": [
            {
                "cliente_source": "erp",
                "cliente_external_id": "123",
                "rol": "Operador",
            }
        ],
    }

    response = await client.post("/locations", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["nombre_oficial"] == "Central Norte"
    assert data["codigo"] == "LOC-001"
    assert data["address"]["calle"] == "Av Principal"
    assert len(data["aliases"]) == 1
    assert len(data["clients"]) == 1
    assert data["es_global"] is False

    payload_update = {
        "nombre_oficial": "Central Norte Actualizada",
        "codigo": "LOC-001",
        "tipo": LocationType.AMBOS.value,
        "activo": False,
        "es_global": True,
        "aliases": [],
        "clients": [],
    }

    response_update = await client.post("/locations", json=payload_update)
    assert response_update.status_code == 201
    updated = response_update.json()
    assert updated["nombre_oficial"] == "Central Norte Actualizada"
    assert updated["tipo"] == LocationType.AMBOS.value
    assert updated["activo"] is False
    assert updated["aliases"] == []
    assert updated["clients"] == []
    assert updated["es_global"] is True


@pytest.mark.asyncio
async def test_list_locations_with_filters(client):
    await client.post(
        "/locations",
        json={
            "nombre_oficial": "Central Uno",
            "codigo": "LOC-101",
            "tipo": LocationType.ORIGEN.value,
            "es_global": False,
            "clients": [
                {
                    "cliente_source": "erp",
                    "cliente_external_id": "123",
                    "rol": "Operador",
                }
            ],
        },
    )

    await client.post(
        "/locations",
        json={
            "nombre_oficial": "Central Dos",
            "codigo": "LOC-102",
            "tipo": LocationType.DESTINO.value,
            "es_global": True,
            "clients": [],
        },
    )

    response = await client.get(
        "/locations",
        params={
            "cliente_source": "erp",
            "cliente_external_id": "123",
            "limit": 10,
            "offset": 0,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    codes = {item["codigo"] for item in data["items"]}
    assert {"LOC-101", "LOC-102"} <= codes
    loc_102 = next(item for item in data["items"] if item["codigo"] == "LOC-102")
    assert loc_102["es_global"] is True
    loc_101 = next(item for item in data["items"] if item["codigo"] == "LOC-101")
    assert loc_101["es_global"] is False


@pytest.mark.asyncio
async def test_get_location_detail(client):
    response = await client.post(
        "/locations",
        json={
            "nombre_oficial": "Central Tercera",
            "codigo": "LOC-201",
            "tipo": LocationType.AMBOS.value,
            "es_global": False,
            "address": {"ciudad_text": "Puebla"},
        },
    )
    location_id = response.json()["id"]

    detail = await client.get(f"/locations/{location_id}")
    assert detail.status_code == 200
    body = detail.json()
    assert body["id"] == location_id
    assert body["address"]["ciudad_text"] == "Puebla"


@pytest.mark.asyncio
async def test_create_location_without_tipo_defaults_to_ambos(client):
    payload = {
        "nombre_oficial": "Sin Tipo",
        "codigo": "LOC-301",
        "es_global": False,
        "clients": [],
    }

    response = await client.post("/locations", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["tipo"] == LocationType.AMBOS.value


@pytest.mark.asyncio
async def test_list_locations_by_client_endpoint(client):
    await client.post(
        "/locations",
        json={
            "nombre_oficial": "Central Cliente",
            "codigo": "LOC-401",
            "es_global": False,
            "clients": [
                {
                    "cliente_source": "crm",
                    "cliente_external_id": "99",
                    "rol": "Operador",
                }
            ],
        },
    )

    await client.post(
        "/locations",
        json={
            "nombre_oficial": "Central Global",
            "codigo": "LOC-ALL",
            "es_global": True,
            "clients": [],
        },
    )

    response = await client.get("/clients/crm/99/locations")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    codes = [item["codigo"] for item in data["items"]]
    assert "LOC-401" in codes
    assert "LOC-ALL" in codes
    loc_all = next(item for item in data["items"] if item["codigo"] == "LOC-ALL")
    assert loc_all["es_global"] is True
    loc_401 = next(item for item in data["items"] if item["codigo"] == "LOC-401")
    assert loc_401["es_global"] is False


@pytest.mark.asyncio
async def test_delete_location(client):
    response = await client.post(
        "/locations",
        json={
            "nombre_oficial": "Central Borrar",
            "codigo": "LOC-DELETE",
            "es_global": False,
        },
    )
    assert response.status_code == 201
    location_id = response.json()["id"]

    delete_response = await client.delete(f"/locations/{location_id}")
    assert delete_response.status_code == 204

    detail_after_delete = await client.get(f"/locations/{location_id}")
    assert detail_after_delete.status_code == 404

    second_delete = await client.delete(f"/locations/{location_id}")
    assert second_delete.status_code == 404
