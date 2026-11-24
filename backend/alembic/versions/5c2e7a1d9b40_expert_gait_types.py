"""expert gait types: record walk test, exercise dosage, link rule target

Revision ID: 5c2e7a1d9b40
Revises: 081863001cb4
Create Date: 2026-11-17 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '5c2e7a1d9b40'
down_revision = '081863001cb4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('record', sa.Column('walk_test', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('exercise', sa.Column('dosage', sa.Text(), server_default='', nullable=False))
    op.alter_column('link_rule', 'metric', new_column_name='target')
    op.add_column('link_rule', sa.Column('recheck', postgresql.JSONB(astext_type=sa.Text()),
                                         server_default=sa.text("'[]'::jsonb"), nullable=False))
    # 연결 대상이 지표에서 보행 유형으로 바뀌어 기존 캐시는 형식이 맞지 않는다.
    op.execute("DELETE FROM analysis_result")


def downgrade() -> None:
    op.drop_column('link_rule', 'recheck')
    op.alter_column('link_rule', 'target', new_column_name='metric')
    op.drop_column('exercise', 'dosage')
    op.drop_column('record', 'walk_test')
