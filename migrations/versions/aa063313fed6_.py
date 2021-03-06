"""empty message

Revision ID: aa063313fed6
Revises: 47928774f34e
Create Date: 2018-11-26 15:23:48.390449

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aa063313fed6'
down_revision = '47928774f34e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ih_user_profile', sa.Column('extra', sa.String(length=128), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('ih_user_profile', 'extra')
    # ### end Alembic commands ###
