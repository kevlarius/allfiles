"""add hashes columns

Revision ID: 9b384916a155
Revises: a306c8ddcbf1
Create Date: 2023-07-10 23:50:11.381853

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "9b384916a155"
down_revision = "a306c8ddcbf1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("file", sa.Column("crc32", sa.String(), nullable=True))
    op.add_column("file", sa.Column("sha1", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("file", "sha1")
    op.drop_column("file", "crc32")
