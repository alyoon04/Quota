"""add users table and user_id foreign keys

Revision ID: 0003
Revises: 0002
Create Date: 2026-03-25 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    op.add_column("plans", sa.Column("user_id", sa.Uuid(), nullable=True))
    op.create_foreign_key("fk_plans_user_id", "plans", "users", ["user_id"], ["id"])

    # Drop the old single-column unique constraint on plans.name, then add a
    # composite (name, user_id) constraint so each user can have their own
    # plans with the same name.
    op.drop_constraint("plans_name_key", "plans", type_="unique")
    op.create_unique_constraint("uq_plans_name_user", "plans", ["name", "user_id"])

    op.add_column("api_keys", sa.Column("user_id", sa.Uuid(), nullable=True))
    op.create_foreign_key("fk_api_keys_user_id", "api_keys", "users", ["user_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint("fk_api_keys_user_id", "api_keys", type_="foreignkey")
    op.drop_column("api_keys", "user_id")

    op.drop_constraint("uq_plans_name_user", "plans", type_="unique")
    op.create_unique_constraint("plans_name_key", "plans", ["name"])
    op.drop_constraint("fk_plans_user_id", "plans", type_="foreignkey")
    op.drop_column("plans", "user_id")

    op.drop_table("users")
