"""brew fermentation steps removed

Revision ID: 44643242c85b
Revises: 4adad2975206
Create Date: 2013-10-18 11:05:03.607463

"""

# revision identifiers, used by Alembic.
revision = '44643242c85b'
down_revision = '4adad2975206'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('brew', u'fermentation_steps')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('brew', sa.Column(u'fermentation_steps', sa.TEXT(), nullable=True))
    ### end Alembic commands ###