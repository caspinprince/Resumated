"""create about_me and last_online columns

Revision ID: 92397c862483
Revises: 3bdb2f1bc1ae
Create Date: 2022-01-02 19:29:50.799457

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "92397c862483"
down_revision = "3bdb2f1bc1ae"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "User_Info", sa.Column(
            "about_me", sa.String(length=1000), nullable=True)
    )
    op.add_column("User_Info", sa.Column(
        "last_online", sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("User_Info", "last_online")
    op.drop_column("User_Info", "about_me")
    # ### end Alembic commands ###
