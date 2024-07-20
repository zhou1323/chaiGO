"""Add receipt filename and url

Revision ID: 1c94acfdf795
Revises: fe6dbadb3293
Create Date: 2024-07-18 16:49:46.295333

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '1c94acfdf795'
down_revision = 'fe6dbadb3293'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('receipt', sa.Column('file_name', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True))
    op.add_column('receipt', sa.Column('file_url', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('receipt', 'file_url')
    op.drop_column('receipt', 'file_name')
    # ### end Alembic commands ###
