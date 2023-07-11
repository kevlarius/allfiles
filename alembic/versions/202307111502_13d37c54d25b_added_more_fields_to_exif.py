"""added more fields to exif

Revision ID: 13d37c54d25b
Revises: 1703d030fd2d
Create Date: 2023-07-11 15:02:09.786757

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "13d37c54d25b"
down_revision = "1703d030fd2d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("exif", sa.Column("gps_altitude", sa.String(), nullable=True))
    op.add_column("exif", sa.Column("exposure_time", sa.String(), nullable=True))
    op.add_column("exif", sa.Column("f_number", sa.String(), nullable=True))
    op.add_column("exif", sa.Column("focal_length", sa.String(), nullable=True))
    op.add_column(
        "exif", sa.Column("focal_length_in_35mm_film", sa.String(), nullable=True)
    )
    op.add_column("exif", sa.Column("orientation", sa.String(), nullable=True))
    op.add_column("exif", sa.Column("software", sa.String(), nullable=True))
    op.add_column("exif", sa.Column("max_aperture_value", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("exif", "max_aperture_value")
    op.drop_column("exif", "software")
    op.drop_column("exif", "orientation")
    op.drop_column("exif", "focal_length_in_35mm_film")
    op.drop_column("exif", "focal_length")
    op.drop_column("exif", "f_number")
    op.drop_column("exif", "exposure_time")
    op.drop_column("exif", "gps_altitude")
