"""Add request description field to file association table

Revision ID: 9ee9b24b0079
Revises: 77e7a228a6bd
Create Date: 2022-01-30 20:30:04.498291

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9ee9b24b0079'
down_revision = '77e7a228a6bd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'Feedback', 'User_Info', ['user_id'], ['id'])
    op.create_foreign_key(None, 'File', 'User_Info', ['user_id'], ['id'])
    op.add_column('FileAssociation', sa.Column('requests', sa.String(length=2000), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('FileAssociation', 'requests')
    op.drop_constraint(None, 'File', type_='foreignkey')
    op.drop_constraint(None, 'Feedback', type_='foreignkey')
    # ### end Alembic commands ###