"""fix file association

Revision ID: 6b683394ca2b
Revises: 
Create Date: 2022-01-26 01:45:36.502847

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6b683394ca2b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('File',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(length=250), nullable=False),
    sa.Column('last_modified', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('User_Info',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=64), nullable=True),
    sa.Column('last_name', sa.String(length=64), nullable=True),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=100), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('google_id', sa.String(length=64), nullable=True),
    sa.Column('about_me', sa.String(length=1000), nullable=True),
    sa.Column('headline', sa.String(length=250), nullable=True),
    sa.Column('last_online', sa.DateTime(), nullable=True),
    sa.Column('pfp_id', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('pfp_id')
    )
    op.create_index(op.f('ix_User_Info_email'), 'User_Info', ['email'], unique=True)
    op.create_index(op.f('ix_User_Info_google_id'), 'User_Info', ['google_id'], unique=True)
    op.create_index(op.f('ix_User_Info_username'), 'User_Info', ['username'], unique=True)
    op.create_table('FileAssociation',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('file_id', sa.Integer(), nullable=False),
    sa.Column('user_status', sa.String(length=50), nullable=False),
    sa.Column('file_status', sa.String(length=25), nullable=False),
    sa.ForeignKeyConstraint(['file_id'], ['File.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['User_Info.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'file_id')
    )
    op.create_table('Settings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(length=50), nullable=False),
    sa.Column('value', sa.String(length=50), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['User_Info.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Settings')
    op.drop_table('FileAssociation')
    op.drop_index(op.f('ix_User_Info_username'), table_name='User_Info')
    op.drop_index(op.f('ix_User_Info_google_id'), table_name='User_Info')
    op.drop_index(op.f('ix_User_Info_email'), table_name='User_Info')
    op.drop_table('User_Info')
    op.drop_table('File')
    # ### end Alembic commands ###
