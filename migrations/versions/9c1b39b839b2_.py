"""empty message

Revision ID: 9c1b39b839b2
Revises: 6879c4b69864
Create Date: 2020-10-30 13:21:21.135933

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9c1b39b839b2'
down_revision = '6879c4b69864'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('light',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('starting_time', sa.Time(), nullable=True),
    sa.Column('duration', sa.Time(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('light')
    # ### end Alembic commands ###
