"""add celery tables

Revision ID: 4fad0580aa59
Revises: 5451775580c9
Create Date: 2024-10-10 13:12:49.771274

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '4fad0580aa59'
down_revision = '5451775580c9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('celery_taskmeta',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('task_id', sqlmodel.sql.sqltypes.AutoString(length=155), nullable=True),
    sa.Column('status', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
    sa.Column('result', sa.LargeBinary(), nullable=True),
    sa.Column('date_done', sa.DateTime(), nullable=True),
    sa.Column('traceback', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=155), nullable=True),
    sa.Column('args', sa.LargeBinary(), nullable=True),
    sa.Column('kwargs', sa.LargeBinary(), nullable=True),
    sa.Column('worker', sqlmodel.sql.sqltypes.AutoString(length=155), nullable=True),
    sa.Column('retries', sa.Integer(), nullable=True),
    sa.Column('queue', sqlmodel.sql.sqltypes.AutoString(length=155), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('task_id')
    )
    op.create_table('celery_tasksetmeta',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('taskset_id', sqlmodel.sql.sqltypes.AutoString(length=155), nullable=True),
    sa.Column('result', sa.LargeBinary(), nullable=True),
    sa.Column('date_done', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('taskset_id')
    )
    op.add_column('receipt', sa.Column('task_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.alter_column('receipt', 'category',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('receipt', 'category',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)
    op.drop_column('receipt', 'task_id')
    op.drop_table('celery_tasksetmeta')
    op.drop_table('celery_taskmeta')
    # ### end Alembic commands ###
