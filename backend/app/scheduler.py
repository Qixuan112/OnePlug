"""
插件版本自动同步调度器。

使用 APScheduler 3.x 的 BackgroundScheduler 周期性触发
``sync_all_approved_plugins()``。多 worker 部署下用 MySQL ``GET_LOCK``
保证同一时刻只有一个 worker 执行同步；SQLite / dev / testing 单进程无需加锁。

调度器线程不在请求上下文内，因此 ``_sync_job`` 通过 ``_app.app_context()``
显式进入应用上下文后再访问数据库。整个 job 用 try/except 兜底，绝不向调度器
抛异常（否则 APScheduler 会反复打错误日志并可能停止调度）。
"""

import atexit
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import text

from app import db

logger = logging.getLogger(__name__)

_scheduler = None
_app = None

_LOCK_NAME = 'oneplug_plugin_sync'


def _run_sync():
    """在已激活的 app context 内执行一次全量同步，带多 worker 互斥。"""
    from app.services.plugin_service import sync_all_approved_plugins

    engine = db.engine
    if engine.dialect.name != 'mysql':
        # SQLite / dev / testing：单进程，无需分布式锁
        sync_all_approved_plugins()
        return

    with engine.connect() as conn:
        acquired = conn.execute(
            text(f"SELECT GET_LOCK('{_LOCK_NAME}', 0)")
        ).scalar()
        if acquired != 1:
            # 其它 worker 正在执行同步，本轮跳过
            return
        try:
            sync_all_approved_plugins()
        finally:
            conn.execute(text(f"SELECT RELEASE_LOCK('{_LOCK_NAME}')"))


def _sync_job():
    """调度器触发的同步任务入口；绝不向调度器抛异常。"""
    global _app
    if _app is None:
        return
    try:
        with _app.app_context():
            _run_sync()
    except Exception as e:
        logger.error(f"Plugin sync job failed: {e}", exc_info=True)


def init_scheduler(app):
    """初始化并启动后台调度器（幂等）。

    - ``PLUGIN_SYNC_ENABLED`` 为 False 时直接返回（testing 默认关闭）。
    - 已初始化过则直接返回。
    - 间隔取 ``PLUGIN_SYNC_INTERVAL_MINUTES``（默认 60）。
    """
    global _scheduler, _app
    if not app.config.get('PLUGIN_SYNC_ENABLED'):
        return
    if _scheduler is not None:
        return

    _app = app
    interval_minutes = app.config.get('PLUGIN_SYNC_INTERVAL_MINUTES', 60)
    if not isinstance(interval_minutes, (int, float)) or interval_minutes < 1:
        logger.warning(
            f"Invalid PLUGIN_SYNC_INTERVAL_MINUTES={interval_minutes!r}, falling back to 60"
        )
        interval_minutes = 60

    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(
        _sync_job,
        IntervalTrigger(minutes=interval_minutes),
        id='plugin_sync',
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown(wait=False))
    _scheduler = scheduler


def trigger_sync_now(app):
    """手动触发一次全量同步（后台线程执行，立即返回）。

    复用 _run_sync 的多 worker 互斥（GET_LOCK）与 app context。
    供 admin 手动触发接口使用，不依赖 PLUGIN_SYNC_ENABLED 是否开启。
    """
    import threading

    def _runner():
        try:
            with app.app_context():
                _run_sync()
        except Exception as e:
            logger.error(f"Manual plugin sync failed: {e}", exc_info=True)

    threading.Thread(target=_runner, daemon=True).start()
