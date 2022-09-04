"""link subscriptions and groups with a foreign key

Revision ID: 8ec37e58fa18
Revises: 883625aacaf8
Create Date: 2022-09-04 12:56:16.455759

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8ec37e58fa18'
down_revision = '883625aacaf8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('calendar_subscription', schema=None) as batch_op:
        
        batch_op.alter_column('cg_group_id',
                existing_type=sa.INTEGER(),
                nullable=True)
        batch_op.create_foreign_key("calendar_subscription_FK", 'campus_groups', ['cg_group_id'], ['cg_group_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('calendar_subscription', schema=None) as batch_op:
        
        batch_op.drop_constraint("calendar_subscription_FK", type_='foreignkey')
        batch_op.alter_column( 'cg_group_id',
                existing_type=sa.INTEGER(),
                nullable=False)
    # ### end Alembic commands ###