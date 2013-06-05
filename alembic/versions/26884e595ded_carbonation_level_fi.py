"""carbonation level field

Revision ID: 26884e595ded
Revises: 52fb47380a98
Create Date: 2013-06-05 10:31:44.137459

"""

# revision identifiers, used by Alembic.
revision = '26884e595ded'
down_revision = '52fb47380a98'

from alembic import op
import sqlalchemy as sa


def upgrade():
    from brewlog.brewing.choices import CARB_LEVEL_KEYS
    op.add_column('brew', sa.Column('carbonation_level', sa.Enum(*CARB_LEVEL_KEYS)))

def downgrade():
    op.drop_column('brew', 'carbonation_level')
