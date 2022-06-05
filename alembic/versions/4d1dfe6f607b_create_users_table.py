"""create_users_table

Revision ID: 4d1dfe6f607b
Revises: 
Create Date: 2022-06-05 21:09:04.744462

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '4d1dfe6f607b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('full_name', sa.String(length=255), nullable=False),
    sa.Column('email_activated_at', sa.TIMESTAMP(), nullable=True),
    sa.Column('client_key', sa.String(length=255), nullable=False),
    sa.Column('client_secret', sa.String(length=255), nullable=False),
    sa.Column('is_client', sa.Boolean(), server_default='1', nullable=True),
    sa.Column('balance', mysql.DOUBLE(asdecimal=True), server_default='0.0', nullable=True),
    sa.Column('is_active', sa.Boolean(), server_default='1', nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('client_key'),
    sa.UniqueConstraint('client_secret'),
    sa.UniqueConstraint('email')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    # ### end Alembic commands ###