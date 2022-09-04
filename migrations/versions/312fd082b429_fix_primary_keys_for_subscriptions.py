"""store campus group information

Revision ID: 312fd082b429
Revises: cd745c6470db
Create Date: 2022-09-04 11:30:08.682519

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '312fd082b429'
down_revision = 'cd745c6470db'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('calendar_subscription', schema=None) as batch_op:
        # batch_op.add_column(sa.Column('street', sa.String(length=50), nullable=True))
        batch_op.alter_column('discord_server_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('cg_group_id',
               existing_type=sa.INTEGER(),
               nullable=False)


def downgrade() -> None:
    with op.batch_alter_table('calendar_subscription', schema=None) as batch_op:
        # batch_op.add_column(sa.Column('street', sa.String(length=50), nullable=True))
        batch_op.alter_column('discord_server_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('cg_group_id',
               existing_type=sa.INTEGER(),
               nullable=True)
