"""added index

Revision ID: 1be3b8bc00d5
Revises: 9b384916a155
Create Date: 2023-07-10 23:58:24.824155

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "1be3b8bc00d5"
down_revision = "9b384916a155"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(op.f("ix_file_crc32"), "file", ["crc32"], unique=False)
    op.create_index(op.f("ix_file_name"), "file", ["name"], unique=False)
    op.create_index(op.f("ix_file_sha1"), "file", ["sha1"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_file_sha1"), table_name="file")
    op.drop_index(op.f("ix_file_name"), table_name="file")
    op.drop_index(op.f("ix_file_crc32"), table_name="file")
