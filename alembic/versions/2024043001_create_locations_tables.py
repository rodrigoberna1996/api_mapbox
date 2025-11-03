"""create locations tables"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "2024043001"
down_revision = None
branch_labels = None
depends_on = None


location_type_enum = sa.Enum(
    "Origen", "Destino", "Ambos", name="location_type", native_enum=False
)


def upgrade() -> None:
    op.create_table(
        "localidades",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("nombre_oficial", sa.String(length=255), nullable=False, unique=True),
        sa.Column("codigo", sa.String(length=50), nullable=False, unique=True),
        sa.Column(
            "tipo",
            location_type_enum,
            nullable=False,
            server_default=sa.text("'Ambos'"),
        ),
        sa.Column(
            "activo",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    op.create_table(
        "direcciones",
        sa.Column(
            "localidad_id",
            sa.Integer(),
            sa.ForeignKey("localidades.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("calle", sa.String(length=255), nullable=True),
        sa.Column("colonia", sa.String(length=255), nullable=True),
        sa.Column("ciudad_text", sa.String(length=255), nullable=True),
        sa.Column("estado_text", sa.String(length=255), nullable=True),
        sa.Column("cp", sa.String(length=20), nullable=True),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("lng", sa.Float(), nullable=True),
        sa.Column("referencia", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    op.create_table(
        "localidad_alias",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column(
            "localidad_id",
            sa.Integer(),
            sa.ForeignKey("localidades.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("alias", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.UniqueConstraint("localidad_id", "alias", name="uq_localidad_alias"),
    )

    op.create_table(
        "localidad_clientes",
        sa.Column(
            "localidad_id",
            sa.Integer(),
            sa.ForeignKey("localidades.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("cliente_source", sa.String(length=50), primary_key=True, nullable=False),
        sa.Column("cliente_external_id", sa.String(length=100), primary_key=True, nullable=False),
        sa.Column("rol", sa.String(length=50), primary_key=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    op.create_table(
        "geocoding_cache",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column(
            "localidad_id",
            sa.Integer(),
            sa.ForeignKey("localidades.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("external_id", sa.String(length=100), nullable=False),
        sa.Column("raw_json", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.UniqueConstraint("localidad_id", "provider", "external_id", name="uq_geocoding"),
    )


def downgrade() -> None:
    op.drop_table("geocoding_cache")
    op.drop_table("localidad_clientes")
    op.drop_table("localidad_alias")
    op.drop_table("direcciones")
    op.drop_table("localidades")
