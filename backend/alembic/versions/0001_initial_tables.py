"""initial tables

Revision ID: 0001
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "plans",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("default_rpm", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "api_keys",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("key_hash", sa.String(length=64), nullable=False),
        sa.Column("label", sa.String(length=255), nullable=False),
        sa.Column("plan_id", sa.Uuid(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["plan_id"], ["plans.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key_hash"),
    )


def downgrade() -> None:
    op.drop_table("api_keys")
    op.drop_table("plans")
