"""convert_source_enum_to_varchar

Revision ID: 41aa4bb49dd3
Revises: 3d05f5f5c850
Create Date: 2026-09-22 12:37:48.402506

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '41aa4bb49dd3'
down_revision: Union[str, Sequence[str], None] = '3d05f5f5c850'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TABLE products ALTER COLUMN source TYPE VARCHAR USING source::text")
    op.execute("DROP TYPE IF EXISTS sourceenum")

def downgrade() -> None:
    """Downgrade schema."""
    op.execute("CREATE TYPE sourceenum AS ENUM ('amazon', 'ubuy')")
    op.execute("ALTER TABLE products ALTER COLUMN source TYPE sourceenum USING source::sourceenum")
