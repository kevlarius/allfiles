"""added audio meta data

Revision ID: ddacc68da0bc
Revises: 13d37c54d25b
Create Date: 2023-07-11 16:33:26.010933

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ddacc68da0bc'
down_revision = '13d37c54d25b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('audiometa',
    sa.Column('id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('artist', sa.String(), nullable=True),
    sa.Column('album', sa.String(), nullable=True),
    sa.Column('album_artist', sa.String(), nullable=True),
    sa.Column('track_number', sa.String(), nullable=True),
    sa.Column('year', sa.String(), nullable=True),
    sa.Column('genre', sa.String(), nullable=True),
    sa.Column('sampling_frequency', sa.String(), nullable=True),
    sa.Column('bit_rate', sa.String(), nullable=True),
    sa.Column('duration', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.add_column('file', sa.Column('audio_meta_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_file_audio_meta_id'), 'file', ['audio_meta_id'], unique=False)
    op.create_foreign_key('audio_meta_id', 'file', 'audiometa', ['audio_meta_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('audio_meta_id', 'file', type_='foreignkey')
    op.drop_index(op.f('ix_file_audio_meta_id'), table_name='file')
    op.drop_column('file', 'audio_meta_id')
    op.drop_table('audiometa')
