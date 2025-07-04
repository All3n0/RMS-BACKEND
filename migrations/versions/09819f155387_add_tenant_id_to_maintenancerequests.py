"""Add tenant_id to MaintenanceRequests

Revision ID: 09819f155387
Revises: 64b67687300f
Create Date: 2025-06-24 22:54:44.908597

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '09819f155387'
down_revision = '64b67687300f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('maintenance_requests', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tenant_id', sa.Integer(), nullable=False))
        batch_op.alter_column('cost',
               existing_type=sa.FLOAT(),
               nullable=True)
        batch_op.create_foreign_key('fk_maintenance_requests_tenant_id', 'tenants', ['tenant_id'], ['id'])


    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('maintenance_requests', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.alter_column('cost',
               existing_type=sa.FLOAT(),
               nullable=False)
        batch_op.drop_column('tenant_id')

    # ### end Alembic commands ###
