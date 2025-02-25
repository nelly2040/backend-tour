"""Added full_name to Booking

Revision ID: 0e91efb6631a
Revises: 605e6baa0c3e
Create Date: 2025-02-03 13:14:12.786685

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0e91efb6631a'
down_revision = '605e6baa0c3e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bookings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('full_name', sa.String(length=100), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bookings', schema=None) as batch_op:
        batch_op.drop_column('full_name')

    # ### end Alembic commands ###
