"""add plugin version sync and history

Revision ID: c4e8a1f02d39
Revises: d31988be4862
Create Date: 2026-07-31 10:00:00.000000

新增插件版本自动同步所需的字段与版本历史表：
- plugins 表加 manifest_sha（manifest.json blob SHA，变化检测）、last_synced_at
- 新增 plugin_versions 表，归档每次 manifest 变化产生的版本记录
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c4e8a1f02d39'
down_revision = 'd31988be4862'
branch_labels = None
depends_on = None


def upgrade():
    # plugins 表加字段
    with op.batch_alter_table('plugins', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('manifest_sha', sa.String(length=40), nullable=True,
                      comment='manifest.json 的 blob SHA，用于检测仓库内容是否变化')
        )
        batch_op.add_column(
            sa.Column('last_synced_at', sa.DateTime(), nullable=True,
                      comment='上次从 GitHub 成功同步 manifest 的时间')
        )

    # 版本历史表
    op.create_table('plugin_versions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('plugin_id', sa.Integer(), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=True),
        sa.Column('manifest_sha', sa.String(length=40), nullable=False),
        sa.Column('manifest_snapshot', sa.JSON(), nullable=True),
        sa.Column('github_data_snapshot', sa.JSON(), nullable=True),
        sa.Column('synced_at', sa.DateTime(), nullable=False),
        sa.Column('is_current', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['plugin_id'], ['plugins.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('plugin_versions', schema=None) as batch_op:
        batch_op.create_index('ix_plugin_versions_plugin_id', ['plugin_id'], unique=False)
        batch_op.create_index('ix_plugin_versions_is_current', ['is_current'], unique=False)
        batch_op.create_index('idx_plugin_version_plugin_current', ['plugin_id', 'is_current'], unique=False)
        batch_op.create_index('idx_plugin_version_plugin_sha', ['plugin_id', 'manifest_sha'], unique=False)


def downgrade():
    with op.batch_alter_table('plugin_versions', schema=None) as batch_op:
        batch_op.drop_index('idx_plugin_version_plugin_sha')
        batch_op.drop_index('idx_plugin_version_plugin_current')
        batch_op.drop_index('ix_plugin_versions_is_current')
        batch_op.drop_index('ix_plugin_versions_plugin_id')

    op.drop_table('plugin_versions')

    with op.batch_alter_table('plugins', schema=None) as batch_op:
        batch_op.drop_column('last_synced_at')
        batch_op.drop_column('manifest_sha')
