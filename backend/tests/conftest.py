"""
pytest fixtures for OnePlug backend tests.

设计要点
--------
- 使用 ``TestingConfig``（SQLite 内存库 ``sqlite:///:memory:``）。
  SQLAlchemy 2.0 对 ``:memory:`` 默认使用 ``StaticPool``，即整个 app 生命周期
  复用同一条连接，因此 ``db.create_all()`` 建的表在同一个 app context 内
  对后续 session/请求都可见。
- 每个 ``app`` fixture 都是 function scope：每次测试调用 ``create_app('testing')``
  会经由 ``db.init_app(app)`` 建立一个全新 engine + 全新 ``StaticPool`` 连接，
  也就是一个全新的空内存库，天然实现测试隔离，无需手工清表。
- 不修改 ``TestingConfig``，不碰真实数据库。
"""

import pytest

from app import create_app, db
from app.models.user import User, UserRole
from app.models.plugin import Plugin, PluginStatus


@pytest.fixture
def app():
    """每个测试创建一个全新的 testing app + 空的内存库。

    yield 期间 app context 始终处于激活状态，方便测试直接调用 service 层。
    """
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Flask test client（请求在进程内、同线程执行，复用同一内存库连接）。"""
    return app.test_client()


@pytest.fixture
def db_session(app):
    """绑定到当前 testing app 内存库的 SQLAlchemy session。"""
    return db.session


@pytest.fixture
def sample_user(app):
    """一个 developer 用户，作为示例插件的 author。"""
    user = User(github_id='11111', username='sampledev', role=UserRole.developer)
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def sample_plugin(app, sample_user):
    """一个 approved 的 Plugin，repo_url 指向 https://github.com/owner/repo。

    manifest_sha / last_synced_at 均为 None，代表尚未做过首次同步，
    便于在测试里按需设置初始状态。
    """
    plugin = Plugin(
        name='Sample Plugin',
        description='A sample approved plugin for testing sync.',
        repo_url='https://github.com/owner/repo',
        author_id=sample_user.id,
        status=PluginStatus.approved,
    )
    db.session.add(plugin)
    db.session.commit()
    return plugin
