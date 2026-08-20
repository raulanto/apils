"""Auditoria de refresh tokens: rotation chain, device e ip

Revision ID: c468e8c51873
Revises: 85a1fbaba745
Create Date: 2026-08-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c468e8c51873'
down_revision: Union[str, Sequence[str], None] = '85a1fbaba745'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # batch mode: SQLite can't ALTER in constraints directly, Postgres just runs them as-is.
    with op.batch_alter_table('refresh_tokens') as batch_op:
        batch_op.add_column(sa.Column('replaced_by', sa.String(length=36), nullable=True))
        batch_op.add_column(sa.Column('device_info', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('ip_address', sa.String(length=45), nullable=True))
        batch_op.create_foreign_key(
            'fk_refresh_tokens_replaced_by',
            'refresh_tokens',
            ['replaced_by'], ['id'],
            ondelete='SET NULL',
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('refresh_tokens') as batch_op:
        batch_op.drop_constraint('fk_refresh_tokens_replaced_by', type_='foreignkey')
        batch_op.drop_column('ip_address')
        batch_op.drop_column('device_info')
        batch_op.drop_column('replaced_by')
