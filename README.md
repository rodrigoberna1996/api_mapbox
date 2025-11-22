# Localidades Microservicio

Microservicio en FastAPI (Python 3.12) con arquitectura limpia para gestionar localidades y su información relacionada (direcciones, alias y referencias de clientes). Persiste los datos en PostgreSQL usando SQLAlchemy 2.0 async y cuenta con migraciones mediante Alembic.

## Características

- Arquitectura hexagonal/limpia (domain, application, infrastructure, entrypoints).
- Endpoints REST completos para CRUD y relaciones de localidades.
- Validaciones con Pydantic v2 (lat/lng, nombre y código únicos, tipos permitidos).
- Persistencia asincrónica con SQLAlchemy 2.0 + asyncpg.
- Migraciones iniciales configuradas con Alembic.
- Dockerfile y docker-compose con servicios de API, PostgreSQL y Adminer.
- Pruebas asíncronas con pytest + httpx.

## Requisitos

- Python 3.12+
- PostgreSQL 13+
- (Opcional) Docker y Docker Compose v2

## Configuración local con entorno virtual

```bash
python3.12 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

Crea un archivo `.env` en la raíz (reutilizado por la aplicación y docker-compose) con al menos:

```env
API_MAPBOX_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/locations
API_MAPBOX_APP_NAME=locations-service
API_MAPBOX_DEBUG=true
```

## Migraciones (Alembic)

Inicializa la base y aplica migraciones:

```bash
alembic upgrade head
```

Para generar nuevas migraciones después de modificar los modelos:

```bash
alembic revision --autogenerate -m "mensaje descriptivo"
alembic upgrade head
```

## Ejecución del servidor

Con el entorno virtual activo:

```bash
uvicorn app.main:app --reload
```

La API expone:

- `POST /locations`
- `GET /locations`
- `GET /locations/{id}`
- `PUT /locations/{id}`
- `PUT /locations/{id}/address`
- `POST /locations/{id}/aliases`
- `DELETE /locations/{id}/aliases/{aliasId}`
- `POST /locations/{id}/clients`
- `DELETE /locations/{id}/clients`
- `GET /locations/by-client/{clienteSource}/{clienteExternalId}`
- `GET /health`

## Uso con Docker

```bash
docker compose up --build
```

Servicios disponibles:

- API: http://localhost:8000 (documentación automática en `/docs`)
- PostgreSQL: puerto 5432 (usuario/postgres, contraseña/postgres, DB `locations`)
- Adminer: http://localhost:8080 (conéctate con los datos anteriores)

Aplica migraciones dentro del contenedor de la API:

```bash
docker compose exec api alembic upgrade head
```

## Pruebas

```bash
pytest
```

Las pruebas usan SQLite asíncrono en memoria para validar flujos de creación, listado y búsqueda de localidades.

## Estructura principal

- `app/core`: configuración y utilidades.
- `app/domain`: entidades de dominio y contratos de repositorio.
- `app/application`: DTOs, casos de uso y mapeadores.
- `app/infrastructure`: adaptadores (modelos SQLAlchemy, repositorios, DB).
- `app/entrypoints`: routers FastAPI (HTTP).
- `alembic`: configuración y migraciones de base de datos.
- `tests`: pruebas automatizadas con pytest + httpx.
