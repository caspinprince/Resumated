"""Add table for files, create relationship between file and user tables

Revision ID: a63fddba4104
Revises: abec6543f0ce
Create Date: 2022-01-20 01:21:53.978193

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a63fddba4104'
down_revision = 'abec6543f0ce'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('File', sa.Column('user_id', sa.Integer(), nullable=False))
    op.alter_column('File', 'filename',
               existing_type=mysql.VARCHAR(length=100),
               nullable=False)
    op.create_foreign_key(None, 'File', 'User_Info', ['user_id'], ['id'])
    op.create_unique_constraint(None, 'User_Info', ['pfp_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'User_Info', type_='unique')
    op.drop_constraint(None, 'File', type_='foreignkey')
    op.alter_column('File', 'filename',
               existing_type=mysql.VARCHAR(length=100),
               nullable=True)
    op.drop_column('File', 'user_id')
    # ### end Alembic commands ###
