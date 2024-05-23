"""empty message

Revision ID: a7ed1fbd9a4f
Revises: dc9e1916a3f1
Create Date: 2024-05-23 09:11:17.648828

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a7ed1fbd9a4f'
down_revision = 'dc9e1916a3f1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.add_column(sa.Column('product_image', sa.String(length=1000), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.drop_column('product_image')

    # ### end Alembic commands ###
