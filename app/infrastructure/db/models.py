"""SQLAlchemy ORM models for locations."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.domain.models.location import LocationType
from app.infrastructure.db.base import Base


class LocationModel(Base):
    __tablename__ = "localidades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_oficial: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    tipo: Mapped[LocationType] = mapped_column(
        Enum(LocationType, name="location_type", native_enum=False),
        nullable=False,
        default=LocationType.AMBOS,
        server_default=LocationType.AMBOS.value,
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    es_global: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    address: Mapped["AddressModel | None"] = relationship(
        back_populates="location", cascade="all, delete-orphan", uselist=False
    )
    aliases: Mapped[list["LocationAliasModel"]] = relationship(
        back_populates="location", cascade="all, delete-orphan"
    )
    clients: Mapped[list["LocationClientModel"]] = relationship(
        back_populates="location", cascade="all, delete-orphan"
    )
    geocoding_cache: Mapped[list["GeocodingCacheModel"]] = relationship(
        back_populates="location", cascade="all, delete-orphan"
    )


class AddressModel(Base):
    __tablename__ = "direcciones"

    localidad_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("localidades.id", ondelete="CASCADE"),
        primary_key=True,
    )
    calle: Mapped[str | None] = mapped_column(String(255))
    colonia: Mapped[str | None] = mapped_column(String(255))
    ciudad_text: Mapped[str | None] = mapped_column(String(255))
    estado_text: Mapped[str | None] = mapped_column(String(255))
    cp: Mapped[str | None] = mapped_column(String(20))
    lat: Mapped[float | None] = mapped_column(Float)
    lng: Mapped[float | None] = mapped_column(Float)
    referencia: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    location: Mapped[LocationModel] = relationship(back_populates="address")


class LocationAliasModel(Base):
    __tablename__ = "localidad_alias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    localidad_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("localidades.id", ondelete="CASCADE"), nullable=False
    )
    alias: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    location: Mapped[LocationModel] = relationship(back_populates="aliases")

    __table_args__ = (
        UniqueConstraint("localidad_id", "alias", name="uq_localidad_alias"),
    )


class LocationClientModel(Base):
    __tablename__ = "localidad_clientes"

    localidad_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("localidades.id", ondelete="CASCADE"), primary_key=True
    )
    cliente_source: Mapped[str] = mapped_column(String(50), primary_key=True)
    cliente_external_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    rol: Mapped[str] = mapped_column(String(50), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    location: Mapped[LocationModel] = relationship(back_populates="clients")


class GeocodingCacheModel(Base):
    __tablename__ = "geocoding_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    localidad_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("localidades.id", ondelete="CASCADE"), nullable=False
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    external_id: Mapped[str] = mapped_column(String(100), nullable=False)
    raw_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    location: Mapped[LocationModel] = relationship(back_populates="geocoding_cache")

    __table_args__ = (
        UniqueConstraint("localidad_id", "provider", "external_id", name="uq_geocoding"),
    )
