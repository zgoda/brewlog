"""No IPBoard id in users table

Revision ID: 133b28b9cbdd
Revises: 3b5f8e086391
Create Date: 2013-07-01 10:32:01.563644

"""

# revision identifiers, used by Alembic.
revision = '133b28b9cbdd'
down_revision = '3b5f8e086391'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_column('brewer_profile', 'ipboard_topic_id')


def downgrade():
    op.add_column('brewer_profile', sa.Column('ipboard_topic_id', sa.String(20)))
