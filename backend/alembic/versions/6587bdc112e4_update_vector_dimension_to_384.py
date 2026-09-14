"""update vector dimension to 384

Revision ID: 6587bdc112e4
Revises: af06d60ab0a2
Create Date: 2026-09-14 00:21:31.409194

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6587bdc112e4'
down_revision: Union[str, Sequence[str], None] = 'af06d60ab0a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TABLE transcript_chunks ALTER COLUMN embedding TYPE vector(384);")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TABLE transcript_chunks ALTER COLUMN embedding TYPE vector(1536);")
