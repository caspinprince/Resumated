"""create user table

Revision ID: 3bdb2f1bc1ae
Revises: 
Create Date: 2022-01-02 19:28:47.052668

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3bdb2f1bc1ae"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "User_Info",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("first_name", sa.String(length=64), nullable=True),
        sa.Column("last_name", sa.String(length=64), nullable=True),
        sa.Column("username", sa.String(length=64), nullable=True),
        sa.Column("email", sa.String(length=100), nullable=True),
        sa.Column("password_hash", sa.String(length=128), nullable=True),
        sa.Column("google_id", sa.String(length=64), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_User_Info_email"),
                    "User_Info", ["email"], unique=True)
    op.create_index(
        op.f("ix_User_Info_google_id"), "User_Info", ["google_id"], unique=True
    )
    op.create_index(
        op.f("ix_User_Info_username"), "User_Info", ["username"], unique=True
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_User_Info_username"), table_name="User_Info")
    op.drop_index(op.f("ix_User_Info_google_id"), table_name="User_Info")
    op.drop_index(op.f("ix_User_Info_email"), table_name="User_Info")
    op.drop_table("User_Info")
    # ### end Alembic commands ###
