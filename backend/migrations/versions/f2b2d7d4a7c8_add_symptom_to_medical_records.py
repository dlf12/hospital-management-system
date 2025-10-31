"""add symptom column to medical_records

Revision ID: f2b2d7d4a7c8
Revises: c9df3333e3bb
Create Date: 2025-10-31 15:30:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f2b2d7d4a7c8'
down_revision = 'c9df3333e3bb'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('medical_records') as batch_op:
        batch_op.add_column(sa.Column('symptom', sa.Text(), nullable=True))


def downgrade():
    with op.batch_alter_table('medical_records') as batch_op:
        batch_op.drop_column('symptom')


