"""Added pfp_id column

Revision ID: abec6543f0ce
Revises: fba340536cca
Create Date: 2022-01-17 22:10:14.475399

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "abec6543f0ce"
down_revision = "fba340536cca"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("User_Info", sa.Column(
        "pfp_id", sa.String(length=50), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("User_Info", "pfp_id")
    # ### end Alembic commands ###
