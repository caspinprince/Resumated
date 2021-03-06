"""add timestamp to file association table

Revision ID: 347748a03c6a
Revises: 456998b7e55a
Create Date: 2022-02-11 20:03:38.404946

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '347748a03c6a'
down_revision = '456998b7e55a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('FileAssociation', sa.Column('timestamp', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('FileAssociation', 'timestamp')
    # ### end Alembic commands ###
