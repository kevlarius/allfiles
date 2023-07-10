"""change size data type

Revision ID: 71349f95d0cc
Revises: 
Create Date: 2023-07-10 01:46:09.766648

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "71349f95d0cc"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "file",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("size", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("file")
