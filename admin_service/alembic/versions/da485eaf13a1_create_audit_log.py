"""create audit_log

Revision ID: da485eaf13a1
Revises: 
Create Date: 2025-04-30 17:58:10.550885

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'da485eaf13a1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'audit_log',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('admin_id', sa.Integer, nullable=False),
        sa.Column('action', sa.String, nullable=False),
        sa.Column('target_id', sa.Integer, nullable=False),
        sa.Column('reason', sa.String),
        sa.Column('timestamp', sa.DateTime, nullable=False, server_default=sa.func.now())
    )

def downgrade():
    op.drop_table('audit_log')
