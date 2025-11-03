"""Convert UUID identifiers to integer based ones."""
from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op


# revision identifiers, used by Alembic.
revision = "2025101101"
down_revision = "2024060301"
branch_labels = None
depends_on = None


def _column_is_uuid(inspector: sa.Inspector, table: str, column: str) -> bool:
    columns = inspector.get_columns(table)
    try:
        col = next(col for col in columns if col["name"] == column)
    except StopIteration as exc:
        raise RuntimeError(f"Column {column} not found in table {table}") from exc
    return isinstance(col["type"], postgresql.UUID)


def _ensure_sequence(sequence_name: str, table: str, column: str) -> None:
    op.execute(
        sa.text(
            f"DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relkind = 'S' AND relname = :seq) "
            f"THEN EXECUTE 'CREATE SEQUENCE {sequence_name}'; END IF; END $$;"
        ).bindparams(sa.bindparam("seq", sequence_name))
    )
    op.execute(sa.text(f"ALTER SEQUENCE {sequence_name} OWNED BY {table}.{column}"))


def _sync_sequence(sequence_name: str, table: str, column: str) -> None:
    op.execute(
        sa.text(
            f"SELECT setval(:seq, COALESCE((SELECT MAX({column}) FROM {table}), 0) + 1, false)"
        ).bindparams(sa.bindparam("seq", sequence_name))
    )
    op.execute(
        sa.text(f"ALTER TABLE {table} ALTER COLUMN {column} SET DEFAULT nextval(:seq)")
        .bindparams(sa.bindparam("seq", sequence_name))
    )


def _convert_localidades() -> None:
    op.add_column(
        "localidades",
        sa.Column("id_int", sa.Integer(), nullable=True),
    )
    _ensure_sequence("localidades_id_int_seq", "localidades", "id_int")
    op.execute(
        sa.text(
            "UPDATE localidades SET id_int = nextval('localidades_id_int_seq') WHERE id_int IS NULL"
        )
    )
    op.execute(sa.text("ALTER TABLE localidades ALTER COLUMN id_int SET NOT NULL"))


def _convert_direcciones() -> None:
    op.add_column("direcciones", sa.Column("localidad_id_int", sa.Integer(), nullable=True))
    op.execute(
        sa.text(
            """
            UPDATE direcciones d
            SET localidad_id_int = l.id_int
            FROM localidades l
            WHERE d.localidad_id = l.id
            """
        )
    )
    op.execute(sa.text("ALTER TABLE direcciones ALTER COLUMN localidad_id_int SET NOT NULL"))


def _convert_localidad_alias() -> None:
    op.add_column("localidad_alias", sa.Column("id_int", sa.Integer(), nullable=True))
    _ensure_sequence("localidad_alias_id_int_seq", "localidad_alias", "id_int")
    op.execute(
        sa.text(
            """
            UPDATE localidad_alias
            SET id_int = nextval('localidad_alias_id_int_seq')
            WHERE id_int IS NULL
            """
        )
    )
    op.execute(sa.text("ALTER TABLE localidad_alias ALTER COLUMN id_int SET NOT NULL"))

    op.add_column(
        "localidad_alias",
        sa.Column("localidad_id_int", sa.Integer(), nullable=True),
    )
    op.execute(
        sa.text(
            """
            UPDATE localidad_alias a
            SET localidad_id_int = l.id_int
            FROM localidades l
            WHERE a.localidad_id = l.id
            """
        )
    )
    op.execute(
        sa.text("ALTER TABLE localidad_alias ALTER COLUMN localidad_id_int SET NOT NULL")
    )


def _convert_localidad_clientes() -> None:
    op.add_column(
        "localidad_clientes",
        sa.Column("localidad_id_int", sa.Integer(), nullable=True),
    )
    op.execute(
        sa.text(
            """
            UPDATE localidad_clientes c
            SET localidad_id_int = l.id_int
            FROM localidades l
            WHERE c.localidad_id = l.id
            """
        )
    )
    op.execute(
        sa.text("ALTER TABLE localidad_clientes ALTER COLUMN localidad_id_int SET NOT NULL")
    )


def _convert_geocoding_cache() -> None:
    op.add_column("geocoding_cache", sa.Column("id_int", sa.Integer(), nullable=True))
    _ensure_sequence("geocoding_cache_id_int_seq", "geocoding_cache", "id_int")
    op.execute(
        sa.text(
            """
            UPDATE geocoding_cache
            SET id_int = nextval('geocoding_cache_id_int_seq')
            WHERE id_int IS NULL
            """
        )
    )
    op.execute(sa.text("ALTER TABLE geocoding_cache ALTER COLUMN id_int SET NOT NULL"))

    op.add_column(
        "geocoding_cache",
        sa.Column("localidad_id_int", sa.Integer(), nullable=True),
    )
    op.execute(
        sa.text(
            """
            UPDATE geocoding_cache g
            SET localidad_id_int = l.id_int
            FROM localidades l
            WHERE g.localidad_id = l.id
            """
        )
    )
    op.execute(
        sa.text("ALTER TABLE geocoding_cache ALTER COLUMN localidad_id_int SET NOT NULL")
    )


def _drop_constraints() -> None:
    op.drop_constraint("direcciones_pkey", "direcciones", type_="primary")
    op.drop_constraint("direcciones_localidad_id_fkey", "direcciones", type_="foreignkey")

    op.drop_constraint("localidad_alias_pkey", "localidad_alias", type_="primary")
    op.drop_constraint(
        "localidad_alias_localidad_id_fkey", "localidad_alias", type_="foreignkey"
    )
    op.drop_constraint("uq_localidad_alias", "localidad_alias", type_="unique")

    op.drop_constraint("localidad_clientes_pkey", "localidad_clientes", type_="primary")
    op.drop_constraint(
        "localidad_clientes_localidad_id_fkey", "localidad_clientes", type_="foreignkey"
    )

    op.drop_constraint("geocoding_cache_pkey", "geocoding_cache", type_="primary")
    op.drop_constraint(
        "geocoding_cache_localidad_id_fkey", "geocoding_cache", type_="foreignkey"
    )
    op.drop_constraint("uq_geocoding", "geocoding_cache", type_="unique")

    op.drop_constraint("localidades_pkey", "localidades", type_="primary")


def _drop_old_columns() -> None:
    op.drop_column("direcciones", "localidad_id")

    op.drop_column("localidad_alias", "id")
    op.drop_column("localidad_alias", "localidad_id")

    op.drop_column("localidad_clientes", "localidad_id")

    op.drop_column("geocoding_cache", "id")
    op.drop_column("geocoding_cache", "localidad_id")

    op.drop_column("localidades", "id")


def _rename_new_columns() -> None:
    op.alter_column("direcciones", "localidad_id_int", new_column_name="localidad_id")

    op.alter_column("localidad_alias", "id_int", new_column_name="id")
    op.alter_column("localidad_alias", "localidad_id_int", new_column_name="localidad_id")

    op.alter_column("localidad_clientes", "localidad_id_int", new_column_name="localidad_id")

    op.alter_column("geocoding_cache", "id_int", new_column_name="id")
    op.alter_column(
        "geocoding_cache", "localidad_id_int", new_column_name="localidad_id"
    )

    op.alter_column("localidades", "id_int", new_column_name="id")


def _recreate_constraints() -> None:
    _sync_sequence("localidades_id_int_seq", "localidades", "id")
    op.create_primary_key("localidades_pkey", "localidades", ["id"])

    op.create_primary_key("direcciones_pkey", "direcciones", ["localidad_id"])
    op.create_foreign_key(
        "direcciones_localidad_id_fkey",
        "direcciones",
        "localidades",
        ["localidad_id"],
        ["id"],
        ondelete="CASCADE",
    )

    _sync_sequence("localidad_alias_id_int_seq", "localidad_alias", "id")
    op.create_primary_key("localidad_alias_pkey", "localidad_alias", ["id"])
    op.create_foreign_key(
        "localidad_alias_localidad_id_fkey",
        "localidad_alias",
        "localidades",
        ["localidad_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_unique_constraint(
        "uq_localidad_alias", "localidad_alias", ["localidad_id", "alias"]
    )

    op.create_primary_key(
        "localidad_clientes_pkey",
        "localidad_clientes",
        ["localidad_id", "cliente_source", "cliente_external_id", "rol"],
    )
    op.create_foreign_key(
        "localidad_clientes_localidad_id_fkey",
        "localidad_clientes",
        "localidades",
        ["localidad_id"],
        ["id"],
        ondelete="CASCADE",
    )

    _sync_sequence("geocoding_cache_id_int_seq", "geocoding_cache", "id")
    op.create_primary_key("geocoding_cache_pkey", "geocoding_cache", ["id"])
    op.create_foreign_key(
        "geocoding_cache_localidad_id_fkey",
        "geocoding_cache",
        "localidades",
        ["localidad_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_unique_constraint(
        "uq_geocoding", "geocoding_cache", ["localidad_id", "provider", "external_id"]
    )


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not _column_is_uuid(inspector, "localidades", "id"):
        # Database already uses integer identifiers.
        return

    _convert_localidades()
    _convert_direcciones()
    _convert_localidad_alias()
    _convert_localidad_clientes()
    _convert_geocoding_cache()

    _drop_constraints()
    _drop_old_columns()
    _rename_new_columns()
    _recreate_constraints()


def downgrade() -> None:
    raise NotImplementedError(
        "Downgrading integer identifiers back to UUIDs is not supported automatically."
    )
