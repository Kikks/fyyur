"""empty message

Revision ID: 45ecbdacc22b
Revises: 825a8f5a59b2
Create Date: 2022-08-09 15:31:37.055998

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '45ecbdacc22b'
down_revision = '825a8f5a59b2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('looking_for_venue', sa.Boolean(), nullable=True))
    op.drop_column('Artist', 'looking_for_talent')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('looking_for_talent', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('Artist', 'looking_for_venue')
    # ### end Alembic commands ###
