"""added more fields

Revision ID: a306c8ddcbf1
Revises: 71349f95d0cc
Create Date: 2023-07-10 22:21:25.411564

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "a306c8ddcbf1"
down_revision = "71349f95d0cc"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("file", sa.Column("basename", sa.String(), nullable=False))
    op.add_column("file", sa.Column("extension", sa.String(), nullable=True))
    op.add_column("file", sa.Column("location", sa.String(), nullable=False))
    op.add_column("file", sa.Column("created_at", sa.DateTime(), nullable=False))
    op.add_column("file", sa.Column("edited_at", sa.DateTime(), nullable=False))


def downgrade() -> None:
    op.drop_column("file", "edited_at")
    op.drop_column("file", "created_at")
    op.drop_column("file", "location")
    op.drop_column("file", "extension")
    op.drop_column("file", "basename")
