"""add indexes on api_keys

Revision ID: 0002
Revises: 0001
Create Date: 2026-02-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # key_hash is the hot path: every inbound request hashes the key and looks
    # it up. The unique constraint already creates an implicit index in
    # PostgreSQL, but adding a named one makes it explicit and queryable via
    # pg_indexes.
    op.create_index("ix_api_keys_key_hash", "api_keys", ["key_hash"])

    # plan_id is a foreign key used to join in the rate limiter; without an
    # index this becomes a sequential scan on every request.
    op.create_index("ix_api_keys_plan_id", "api_keys", ["plan_id"])


def downgrade() -> None:
    op.drop_index("ix_api_keys_plan_id", table_name="api_keys")
    op.drop_index("ix_api_keys_key_hash", table_name="api_keys")
