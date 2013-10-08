"""width and height for label templates

Revision ID: 47fdd72c6bb3
Revises: 1eeeae3943d3
Create Date: 2013-10-08 09:39:09.366314

"""

# revision identifiers, used by Alembic.
revision = '47fdd72c6bb3'
down_revision = '1eeeae3943d3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('custom_label_template', sa.Column('height', sa.Integer(), server_default='50', nullable=False))
    op.add_column('custom_label_template', sa.Column('width', sa.Integer(), server_default='90', nullable=False))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('custom_label_template', 'width')
    op.drop_column('custom_label_template', 'height')
    ### end Alembic commands ###
