"""empty message

Revision ID: 6879c4b69864
Revises: 
Create Date: 2020-10-30 10:10:14.316892

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6879c4b69864'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sensors',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sensor_type', sa.Integer(), nullable=True),
    sa.Column('sensor_pin', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('sensor_pin')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('readings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('reading_type', sa.String(length=140), nullable=True),
    sa.Column('reading_value', sa.Numeric(), nullable=True),
    sa.Column('sensor_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['sensor_id'], ['sensors.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('readings')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_table('sensors')
    # ### end Alembic commands ###
