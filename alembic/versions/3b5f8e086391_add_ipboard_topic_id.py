"""add IPBoard topic ID

Revision ID: 3b5f8e086391
Revises: 26884e595ded
Create Date: 2013-06-28 15:18:40.484888

"""

# revision identifiers, used by Alembic.
revision = '3b5f8e086391'
down_revision = '26884e595ded'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('brewer_profile', sa.Column('ipboard_topic_id', sa.String(20)))


def downgrade():
    op.drop_column('brewer_profile', 'ipboard_topic_id')
