"""
Flask-Limiter 限流 bug 的复现 + 修复验证测试（TDD）。

被测契约（修复 agent 在 app/__init__.py 与 app/routes/*.py 中实现）：
1. ``create_app`` 中在 ``app = Flask(__name__)`` 之后套用
   ``ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)``。
2. 公共读端点加 ``@limiter.exempt``：
     - plugins.list_plugins / get_all_plugins_json / get_plugin_detail
       / get_plugin_versions_endpoint / list_developers
     - categories.list_categories
     - __init__.health_check
3. 写接口（submit/auth/admin/reviewer）的限流不变。

当前修复尚未实现，因此：
- A 组用例：默认 50/小时限流会让第 51 次起返回 429 -> 用例失败（TDD 预期态）。
- B 组用例：无 ProxyFix 时 remote_addr 仍为 127.0.0.1 -> 用例失败（TDD 预期态）。
- C 组用例：写接口限流仍在 -> 用例通过（回归保护）。

本文件只做测试，不做业务实现。所有 GitHub 调用均通过 mock，不依赖真实网络。
"""

import inspect
from collections import Counter
from unittest.mock import patch

import pytest
from flask import request


# 默认限流为 50/小时；连续请求数必须显著大于 50，才能在未豁免时触发 429。
REQUEST_COUNT = 100


# ===========================================================================
# A. 公共读端点不应被限流（核心）
# ===========================================================================

class TestPublicReadEndpointsNotRateLimited:
    """公共读端点在连续大量请求下不应出现 429。

    修复前：默认 50/小时限流作用于这些端点，第 51 次起返回 429。
    修复后：这些端点 ``@limiter.exempt``，全部 200。
    """

    @pytest.mark.parametrize('path', [
        '/api/plugins',            # list_plugins
        '/api/plugins/all',        # get_all_plugins_json
        '/api/plugins/developers', # list_developers
        '/api/categories',         # list_categories
        '/health',                 # health_check
    ])
    def test_static_path_no_429(self, client, path):
        statuses = [client.get(path).status_code
                    for _ in range(REQUEST_COUNT)]
        assert 429 not in statuses, (
            f"{path} 出现 {statuses.count(429)} 次 429: {Counter(statuses)}"
        )
        assert statuses.count(200) == REQUEST_COUNT, (
            f"{path} 期望全部 200: {Counter(statuses)}"
        )

    def test_plugin_versions_no_429(self, client, sample_plugin):
        """版本历史端点对 sample_plugin 返回 200（items 可为空）。"""
        path = f'/api/plugins/{sample_plugin.id}/versions'
        statuses = [client.get(path).status_code
                    for _ in range(REQUEST_COUNT)]
        assert 429 not in statuses, (
            f"get_plugin_versions_endpoint 出现 {statuses.count(429)} 次 429: "
            f"{Counter(statuses)}"
        )
        assert statuses.count(200) == REQUEST_COUNT, (
            f"versions 端点期望全部 200: {Counter(statuses)}"
        )

    def test_plugin_detail_no_429(self, client, sample_plugin):
        """详情端点 mock 掉 fetch_github_readme，避免真实网络调用。

        plugins.py 顶部 ``from ... import fetch_github_readme`` 把名字绑定到
        plugins 模块自身，因此 patch 源模块不会影响路由内的调用，必须 patch
        调用方模块 ``app.routes.plugins``。同时 patch 源模块以兼容未来重构。
        """
        path = f'/api/plugins/{sample_plugin.id}'
        with patch('app.routes.plugins.fetch_github_readme',
                   return_value=None), \
                patch('app.services.plugin_service.fetch_github_readme',
                      return_value=None):
            statuses = [client.get(path).status_code
                        for _ in range(REQUEST_COUNT)]
        assert 429 not in statuses, (
            f"get_plugin_detail 出现 {statuses.count(429)} 次 429: "
            f"{Counter(statuses)}"
        )
        assert statuses.count(200) == REQUEST_COUNT, (
            f"detail 端点期望全部 200: {Counter(statuses)}"
        )


# ===========================================================================
# B. ProxyFix 生效
# ===========================================================================

class TestProxyFix:
    """带 X-Forwarded-For 的请求，应用看到的 remote_addr 应为转发 IP。

    注意：任务提示用 ``app.test_request_context(...)`` 断言 ``request.remote_addr``，
    但 ``test_request_context`` 直接由 EnvironBuilder 构造请求上下文，**不会经过
    WSGI 中间件栈**，因此 ProxyFix 永远不会被触发 —— 无论是否修复，
    ``request.remote_addr`` 都不会变成转发 IP（实际为 None）。该写法无法验证
    ProxyFix 是否生效。

    这里改用 test client 发起真实请求（走完整 WSGI 栈，含 ProxyFix），并在
    ``before_request`` 钩子里捕获 ``request.remote_addr``：
      - 修复前（无 ProxyFix）: '127.0.0.1'
      - 修复后（x_for=1）: '203.0.113.7'
    """

    def test_remote_addr_uses_x_forwarded_for(self, app):
        seen = []

        @app.before_request
        def _capture_remote_addr():
            seen.append(request.remote_addr)

        client = app.test_client()
        client.get('/health',
                   headers={'X-Forwarded-For': '203.0.113.7'})

        assert seen, "before_request 钩子未触发，未捕获到 remote_addr"
        assert seen[0] == '203.0.113.7', (
            f"期望 remote_addr='203.0.113.7'，实际 '{seen[0]}'"
            "（修复前为 '127.0.0.1'，说明 ProxyFix 未生效）"
        )


# ===========================================================================
# C. 写接口仍限流（回归保护）
# ===========================================================================

class TestWriteEndpointsStillRateLimited:
    """写/动作接口的显式限流应保留，不被误豁免。"""

    def test_create_plugin_keeps_limiter_decorator(self):
        """源码级断言：developer.create_plugin 上仍挂有 @limiter.limit(...)。"""
        from app.routes import developer

        src = inspect.getsource(developer)
        lines = src.splitlines()

        # 定位 def create_plugin
        idx = next((i for i, ln in enumerate(lines)
                    if ln.lstrip().startswith('def create_plugin')), None)
        assert idx is not None, "developer.py 中未找到 def create_plugin"

        # 向上扫描装饰器块（@ 行与空行），确认存在 @limiter.limit(
        found = False
        j = idx - 1
        while j >= 0:
            stripped = lines[j].strip()
            if stripped.startswith('@'):
                if stripped.startswith('@limiter.limit('):
                    found = True
                    break
                j -= 1
            elif stripped == '':
                j -= 1
            else:
                break
        assert found, "create_plugin 上缺少 @limiter.limit(...) 装饰器"

    def test_create_plugin_returns_429_when_over_limit(self, app, client,
                                                      sample_user):
        """运行时断言：连续提交超过 20/hour 后第 21 次起返回 429。

        sample_user 是 developer 角色（见 conftest），可通过 JWT + 角色校验。
        空 body 会被 create_plugin 提前拒成 400，但 limiter 在视图执行前已计数，
        因此前 20 次返回 400、第 21 次起返回 429。
        """
        from flask_jwt_extended import create_access_token

        token = create_access_token(
            identity=str(sample_user.id),
            additional_claims={
                'user_id': sample_user.id,
                'username': sample_user.username,
                'role': sample_user.role.value,
            },
        )
        headers = {'Authorization': f'Bearer {token}'}

        statuses = [
            client.post('/api/developer/plugins', json={},
                        headers=headers).status_code
            for _ in range(25)
        ]

        # 显式限流 20/hour -> 第 21 次起 429
        assert 429 in statuses, (
            f"create_plugin 未触发限流: {Counter(statuses)}"
        )
        assert statuses.count(429) == 5, (
            f"期望 5 次 429（25 - 20）: {Counter(statuses)}"
        )
        assert statuses.count(400) == 20, (
            f"期望 20 次 400（空 body 放行至 handler）: {Counter(statuses)}"
        )
