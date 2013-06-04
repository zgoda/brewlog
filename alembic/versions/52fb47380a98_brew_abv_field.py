"""brew abv field

Revision ID: 52fb47380a98
Revises: None
Create Date: 2013-06-04 15:30:40.337098

"""

# revision identifiers, used by Alembic.
revision = '52fb47380a98'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('brew', sa.Column('abv', sa.Float(precision=1)))


def downgrade():
    op.drop_column('brew', 'abv')
