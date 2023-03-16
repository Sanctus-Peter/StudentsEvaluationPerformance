"""project attribute

Revision ID: f6851a13e210
Revises: 07b08190e205
Create Date: 2023-03-08 02:59:41.004471

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f6851a13e210'
down_revision = '07b08190e205'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admins',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('reg_date', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('guardians',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('gender', sa.String(), nullable=False),
    sa.Column('address', sa.String(), nullable=False),
    sa.Column('mobile_no', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('reg_date', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('teachers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('gender', sa.String(), nullable=False),
    sa.Column('address', sa.String(), nullable=False),
    sa.Column('mobile_no', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('class_taught', sa.String(), nullable=True),
    sa.Column('subject_taught', sa.String(), nullable=True),
    sa.Column('reg_date', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('news',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('content', sa.String(), nullable=False),
    sa.Column('category', sa.String(), nullable=False),
    sa.Column('image', sa.String(), nullable=True),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.Column('date', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['admins.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('students',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('firstname', sa.String(), nullable=False),
    sa.Column('lastname', sa.String(), nullable=False),
    sa.Column('middlename', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('address', sa.String(), nullable=False),
    sa.Column('gender', sa.String(), nullable=False),
    sa.Column('student_class', sa.String(), nullable=False),
    sa.Column('studentID', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('reg_date', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('teacher_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['parent_id'], ['guardians.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['teacher_id'], ['teachers.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('studentID')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('students')
    op.drop_table('news')
    op.drop_table('teachers')
    op.drop_table('guardians')
    op.drop_table('admins')
    # ### end Alembic commands ###