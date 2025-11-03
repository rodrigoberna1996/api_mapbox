"""add es_global flag to localidades"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "2024060301"
down_revision: Union[str, None] = "2024043001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "localidades",
        sa.Column("es_global", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.execute("UPDATE localidades SET es_global = false")
    op.alter_column("localidades", "es_global", server_default=None)


def downgrade() -> None:
    op.drop_column("localidades", "es_global")
