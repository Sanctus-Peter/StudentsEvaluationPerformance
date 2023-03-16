"""unique attribute

Revision ID: 9756965606ec
Revises: bd606fb354d2
Create Date: 2023-03-07 12:36:27.343783

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9756965606ec'
down_revision = 'bd606fb354d2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('students', 'parent_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('students', 'parent_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###