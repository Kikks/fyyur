"""empty message

Revision ID: 99a2b8e8f775
Revises: 45ecbdacc22b
Create Date: 2022-08-10 01:37:16.840452

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '99a2b8e8f775'
down_revision = '45ecbdacc22b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('Show_venue_id_fkey', 'Show', type_='foreignkey')
    op.drop_constraint('Show_artist_id_fkey', 'Show', type_='foreignkey')
    op.drop_column('Show', 'artist_id')
    op.drop_column('Show', 'venue_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('venue_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('Show', sa.Column('artist_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('Show_artist_id_fkey', 'Show', 'Artist', ['artist_id'], ['id'])
    op.create_foreign_key('Show_venue_id_fkey', 'Show', 'Venue', ['venue_id'], ['id'])
    # ### end Alembic commands ###
