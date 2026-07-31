"""
插件版本自动同步功能的单元测试套件。

被测契约（实现由修复 agent 在 app/services/plugin_service.py 中完成）：
    sync_plugin_from_github(plugin_id: int) -> dict
    sync_all_approved_plugins() -> dict
    get_plugin_versions(plugin_id: int) -> list[dict]

当前这些函数尚未实现，因此测试在运行期会因 AttributeError 而失败 --
这是 TDD 的预期初始状态。本文件只做测试，不做业务实现。
所有 GitHub API 调用均通过 mock 完成，不依赖真实网络。
"""

import base64
import json
import os
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

import pytest
import requests

from app import db
from app.services import plugin_service
from app.models.plugin import Plugin, PluginStatus, PluginVersion
from app.models.user import User, UserRole


# ---------------------------------------------------------------------------
# 辅助函数：构造 GitHub API 的 mock 响应
# ---------------------------------------------------------------------------

def _b64_manifest(manifest_dict: dict) -> str:
    """把 manifest dict 编码成 GitHub contents API 返回的 base64 content 字段。"""
    return base64.b64encode(json.dumps(manifest_dict).encode()).decode()


def _contents_response(sha: str, manifest_dict: dict, status_code: int = 200) -> MagicMock:
    """构造 GET .../contents/manifest.json 的 mock 响应。

    返回 ``{"sha": ..., "content": <base64>, "encoding": "base64"}``。
    """
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = {
        'sha': sha,
        'content': _b64_manifest(manifest_dict),
        'encoding': 'base64',
    }
    return resp


def _repo_response(data: dict | None = None, status_code: int = 200) -> MagicMock:
    """构造 GET .../repos/{owner}/{repo} 的 mock 响应（用于刷新 github_data）。"""
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = data or {
        'stargazers_count': 42,
        'forks_count': 7,
        'updated_at': '2024-05-01T10:00:00Z',
        'open_issues_count': 3,
        'language': 'Python',
        'license': {'name': 'MIT'},
        'description': 'a repo',
        'homepage': 'https://example.com',
    }
    return resp


def _route_get(contents_resp, repo_resp):
    """返回一个用于 patch requests.get 的 side_effect：按 URL 路由到两个响应。

    - URL 含 ``/contents/manifest.json`` -> contents_resp
    - 否则（即 repo endpoint）           -> repo_resp
    """
    def _side_effect(url, *args, **kwargs):
        if '/contents/manifest.json' in url:
            if isinstance(contents_resp, Exception):
                raise contents_resp
            return contents_resp
        if isinstance(repo_resp, Exception):
            raise repo_resp
        return repo_resp
    return _side_effect


def _make_plugin(*, name='P', repo_url='https://github.com/owner/repo',
                 status=PluginStatus.approved, manifest_sha=None,
                 manifest=None, version=None, author_id=None) -> Plugin:
    """在当前 session 里新建并提交一个 Plugin，返回对象。"""
    plugin = Plugin(
        name=name,
        repo_url=repo_url,
        author_id=author_id,
        status=status,
        manifest_sha=manifest_sha,
        manifest=manifest,
        version=version,
    )
    db.session.add(plugin)
    db.session.commit()
    return plugin


# ===========================================================================
# sync_plugin_from_github
# ===========================================================================

class TestSyncPluginFromGithub:
    """sync_plugin_from_github 的用例。"""

    def test_plugin_not_found_returns_failed(self, app):
        """插件不存在时返回 failed，且不发起任何 HTTP 请求。"""
        with patch('app.services.plugin_service.requests.get') as mock_get:
            result = plugin_service.sync_plugin_from_github(99999)

        assert result == {
            'status': 'failed',
            'plugin_id': 99999,
            'error': 'Plugin not found',
        }
        assert mock_get.call_count == 0

    def test_plugin_without_repo_url_returns_failed(self, app, sample_user):
        """插件没有 repo_url 时返回 failed，不发起 HTTP 请求。"""
        plugin = _make_plugin(name='NoRepo', repo_url=None, author_id=sample_user.id)

        with patch('app.services.plugin_service.requests.get') as mock_get:
            result = plugin_service.sync_plugin_from_github(plugin.id)

        assert result['status'] == 'failed'
        assert result['plugin_id'] == plugin.id
        assert isinstance(result.get('error'), str) and result['error']
        assert mock_get.call_count == 0

    def test_contents_api_404_returns_failed_no_db_change(self, app, sample_plugin):
        """contents API 返回 404 时返回 failed，库无变化、无新增版本。"""
        plugin_id = sample_plugin.id
        # 记录初始状态
        before = db.session.get(Plugin, plugin_id)
        before_sha = before.manifest_sha
        before_synced = before.last_synced_at

        with patch('app.services.plugin_service.requests.get',
                   side_effect=_route_get(MagicMock(status_code=404), _repo_response())):
            result = plugin_service.sync_plugin_from_github(plugin_id)

        assert result['status'] == 'failed'
        assert result['plugin_id'] == plugin_id
        assert isinstance(result.get('error'), str) and result['error']

        after = db.session.get(Plugin, plugin_id)
        assert after.manifest_sha == before_sha
        assert after.last_synced_at == before_synced
        # 没有产生任何版本记录
        assert db.session.query(PluginVersion).filter_by(
            plugin_id=plugin_id).count() == 0

    def test_contents_api_request_exception_returns_failed(self, app, sample_plugin):
        """contents API 请求抛 RequestException 时返回 failed。"""
        plugin_id = sample_plugin.id

        with patch('app.services.plugin_service.requests.get',
                   side_effect=_route_get(requests.RequestException('boom'),
                                          _repo_response())):
            result = plugin_service.sync_plugin_from_github(plugin_id)

        assert result['status'] == 'failed'
        assert result['plugin_id'] == plugin_id
        assert isinstance(result.get('error'), str) and result['error']

    def test_sha_unchanged_returns_unchanged_no_write(self, app, sample_plugin):
        """SHA 未变时返回 unchanged，不写库、不新增版本。"""
        old_sha = 'a' * 40
        sample_plugin.manifest_sha = old_sha
        sample_plugin.manifest = {'version': '1.0.0', 'name': 'p'}
        sample_plugin.version = '1.0.0'
        db.session.commit()

        plugin_id = sample_plugin.id
        before_synced = sample_plugin.last_synced_at

        manifest = {'version': '1.0.0', 'name': 'p'}
        with patch('app.services.plugin_service.requests.get',
                   side_effect=_route_get(_contents_response(old_sha, manifest),
                                          _repo_response())) as mock_get:
            result = plugin_service.sync_plugin_from_github(plugin_id)

        assert result == {'status': 'unchanged', 'plugin_id': plugin_id}

        # 没有新增版本
        assert db.session.query(PluginVersion).filter_by(
            plugin_id=plugin_id).count() == 0
        # 插件字段未被改写
        after = db.session.get(Plugin, plugin_id)
        assert after.manifest_sha == old_sha
        assert after.last_synced_at == before_synced
        # repo endpoint 不应被调用（SHA 未变即应提前返回）
        repo_calls = [c for c in mock_get.call_args_list
                      if '/contents/manifest.json' not in (c.args[0] if c.args else '')]
        assert repo_calls == []

    def test_sha_changed_updates_plugin_and_archives_version(self, app, sample_plugin):
        """SHA 变化（已有 manifest_sha）-> updated；校验插件字段、版本归档、old/new_sha。"""
        old_sha = '1' * 40
        new_sha = '2' * 40
        old_manifest = {'version': '1.0.0', 'name': 'p'}
        new_manifest = {'version': '2.0.0', 'name': 'p', 'permissions': ['read']}

        sample_plugin.manifest_sha = old_sha
        sample_plugin.manifest = old_manifest
        sample_plugin.version = '1.0.0'
        db.session.commit()
        plugin_id = sample_plugin.id

        # 预置一条旧的 current 版本
        old_version = PluginVersion(
            plugin_id=plugin_id,
            version='1.0.0',
            manifest_sha=old_sha,
            manifest_snapshot=old_manifest,
            github_data_snapshot={'stars': 1},
            synced_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
            is_current=True,
        )
        db.session.add(old_version)
        db.session.commit()

        with patch('app.services.plugin_service.requests.get',
                   side_effect=_route_get(_contents_response(new_sha, new_manifest),
                                          _repo_response())):
            result = plugin_service.sync_plugin_from_github(plugin_id)

        # 返回值形状
        assert result['status'] == 'updated'
        assert result['plugin_id'] == plugin_id
        assert result['version'] == '2.0.0'
        assert result['old_sha'] == old_sha
        assert result['new_sha'] == new_sha

        # 插件字段已更新
        plugin = db.session.get(Plugin, plugin_id)
        assert plugin.manifest == new_manifest
        assert plugin.version == '2.0.0'
        assert plugin.manifest_sha == new_sha
        assert plugin.github_data is not None
        assert plugin.last_synced_at is not None

        # 版本归档：共 2 条，恰好 1 条 current
        versions = db.session.query(PluginVersion).filter_by(plugin_id=plugin_id).all()
        assert len(versions) == 2
        current = [v for v in versions if v.is_current]
        assert len(current) == 1
        assert current[0].manifest_sha == new_sha
        assert current[0].version == '2.0.0'
        assert current[0].manifest_snapshot == new_manifest
        # 旧版本被置为非 current
        stale = [v for v in versions if not v.is_current]
        assert len(stale) == 1
        assert stale[0].manifest_sha == old_sha
        assert stale[0].is_current is False

    def test_first_sync_manifest_sha_none_updates(self, app, sample_plugin):
        """首次同步（manifest_sha 为 None）-> updated；新增 1 条 current 版本。"""
        new_sha = '3' * 40
        manifest = {'version': '1.0.0', 'name': 'first'}
        plugin_id = sample_plugin.id
        assert sample_plugin.manifest_sha is None

        with patch('app.services.plugin_service.requests.get',
                   side_effect=_route_get(_contents_response(new_sha, manifest),
                                          _repo_response())):
            result = plugin_service.sync_plugin_from_github(plugin_id)

        assert result['status'] == 'updated'
        assert result['plugin_id'] == plugin_id
        assert result['version'] == '1.0.0'
        assert result['old_sha'] is None
        assert result['new_sha'] == new_sha

        versions = db.session.query(PluginVersion).filter_by(plugin_id=plugin_id).all()
        assert len(versions) == 1
        assert versions[0].is_current is True
        assert versions[0].manifest_sha == new_sha

        plugin = db.session.get(Plugin, plugin_id)
        assert plugin.manifest_sha == new_sha
        assert plugin.version == '1.0.0'

    def test_manifest_without_version_field_returns_none_version(self, app, sample_plugin):
        """manifest 没有 version 字段 -> updated 且 version 为 None。"""
        new_sha = '4' * 40
        manifest = {'name': 'no-version', 'entry': 'main.js'}
        plugin_id = sample_plugin.id

        with patch('app.services.plugin_service.requests.get',
                   side_effect=_route_get(_contents_response(new_sha, manifest),
                                          _repo_response())):
            result = plugin_service.sync_plugin_from_github(plugin_id)

        assert result['status'] == 'updated'
        assert result['version'] is None
        assert result['new_sha'] == new_sha

        plugin = db.session.get(Plugin, plugin_id)
        assert plugin.version is None

    def test_repo_api_failure_keeps_update_with_none_github_data(self, app, sample_plugin):
        """repo API 失败但 contents 成功 -> 仍 updated，github_data 为 None。"""
        new_sha = '5' * 40
        manifest = {'version': '1.0.0', 'name': 'repo-fail'}
        plugin_id = sample_plugin.id

        with patch('app.services.plugin_service.requests.get',
                   side_effect=_route_get(_contents_response(new_sha, manifest),
                                          MagicMock(status_code=500))):
            result = plugin_service.sync_plugin_from_github(plugin_id)

        assert result['status'] == 'updated'

        plugin = db.session.get(Plugin, plugin_id)
        assert plugin.github_data is None
        # 即便 github_data 为 None，版本快照仍然落库
        versions = db.session.query(PluginVersion).filter_by(plugin_id=plugin_id).all()
        assert len(versions) == 1
        assert versions[0].github_data_snapshot is None

    def test_github_api_token_sets_authorization_header(self, app, sample_plugin):
        """设置了 GITHUB_API_TOKEN 时，每个 GitHub API 请求都带 Authorization 头。"""
        token = 'ghp-test-token-123'
        new_sha = '6' * 40
        manifest = {'version': '1.0.0', 'name': 'tok'}
        plugin_id = sample_plugin.id

        env = {'GITHUB_API_TOKEN': token}
        with patch.dict(os.environ, env), \
                patch('app.services.plugin_service.requests.get') as mock_get:
            mock_get.side_effect = _route_get(_contents_response(new_sha, manifest),
                                              _repo_response())
            result = plugin_service.sync_plugin_from_github(plugin_id)

        assert result['status'] == 'updated'
        assert mock_get.call_count >= 1
        for call in mock_get.call_args_list:
            headers = call.kwargs.get('headers') or {}
            assert headers.get('Authorization') == f'token {token}', (
                f"GitHub API 调用缺少 Authorization 头: {headers}"
            )


# ===========================================================================
# sync_all_approved_plugins
# ===========================================================================

class TestSyncAllApprovedPlugins:
    """sync_all_approved_plugins 的用例。"""

    def test_mixed_approved_plugins_aggregates_counts_and_skips_non_approved(
        self, app, sample_user
    ):
        """混合 approved 插件（更新/不变/失败）汇总正确；非 approved 不被同步。"""
        # P1: SHA 变化 -> updated
        p1 = _make_plugin(name='up', repo_url='https://github.com/owner/repo-up',
                          manifest_sha='a' * 40, manifest={'version': '1.0.0'},
                          version='1.0.0', author_id=sample_user.id)
        # P2: SHA 不变 -> unchanged
        p2 = _make_plugin(name='same', repo_url='https://github.com/owner/repo-same',
                          manifest_sha='c' * 40, manifest={'version': '1.0.0'},
                          version='1.0.0', author_id=sample_user.id)
        # P3: contents 404 -> failed
        p3 = _make_plugin(name='fail', repo_url='https://github.com/owner/repo-fail',
                          manifest_sha='e' * 40, manifest={'version': '1.0.0'},
                          version='1.0.0', author_id=sample_user.id)
        # P4: 非 approved -> 不应被同步
        p4 = _make_plugin(name='draft', repo_url='https://github.com/owner/repo-draft',
                          status=PluginStatus.draft, author_id=sample_user.id)

        def side_effect(url, *args, **kwargs):
            if '/contents/manifest.json' in url:
                if 'repo-up' in url:
                    return _contents_response('b' * 40, {'version': '2.0.0'})
                if 'repo-same' in url:
                    return _contents_response('c' * 40, {'version': '1.0.0'})
                if 'repo-fail' in url:
                    return MagicMock(status_code=404)
                return MagicMock(status_code=404)
            # repo endpoint
            return _repo_response()

        with patch('app.services.plugin_service.requests.get', side_effect=side_effect) as mock_get:
            result = plugin_service.sync_all_approved_plugins()

        assert result == {'total': 3, 'updated': 1, 'unchanged': 1, 'failed': 1}

        # 非 approved 插件未被同步：没有版本记录、没有 HTTP 调用命中 repo-draft
        assert db.session.query(PluginVersion).filter_by(plugin_id=p4.id).count() == 0
        draft_calls = [c for c in mock_get.call_args_list
                       if 'repo-draft' in (c.args[0] if c.args else '')]
        assert draft_calls == []

        # P1 确实被更新（新版本落库），P2/P3 没有
        assert db.session.query(PluginVersion).filter_by(plugin_id=p1.id).count() == 1
        assert db.session.query(PluginVersion).filter_by(plugin_id=p2.id).count() == 0
        assert db.session.query(PluginVersion).filter_by(plugin_id=p3.id).count() == 0

    def test_one_plugin_raises_counts_as_failed_and_continues(self, app, sample_user):
        """某插件抛异常时计入 failed，其余插件继续同步、整体不中断。"""
        p1 = _make_plugin(name='boom', repo_url='https://github.com/owner/repo-boom',
                          author_id=sample_user.id)
        p2 = _make_plugin(name='ok', repo_url='https://github.com/owner/repo-ok',
                          author_id=sample_user.id)

        def fake_sync(plugin_id):
            if plugin_id == p1.id:
                raise RuntimeError('unexpected boom')
            return {'status': 'unchanged', 'plugin_id': plugin_id}

        # 直接 patch 被调用的单插件同步函数，模拟其中某一个抛异常
        with patch.object(plugin_service, 'sync_plugin_from_github',
                          side_effect=fake_sync):
            result = plugin_service.sync_all_approved_plugins()

        assert result == {'total': 2, 'updated': 0, 'unchanged': 1, 'failed': 1}


# ===========================================================================
# get_plugin_versions
# ===========================================================================

class TestGetPluginVersions:
    """get_plugin_versions 的用例。"""

    def test_returns_versions_sorted_by_synced_at_desc(self, app, sample_plugin):
        """返回按 synced_at 降序的版本历史。"""
        plugin_id = sample_plugin.id
        v1 = PluginVersion(
            plugin_id=plugin_id, version='1.0.0', manifest_sha='1' * 40,
            manifest_snapshot={'version': '1.0.0'},
            synced_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
            is_current=False,
        )
        v2 = PluginVersion(
            plugin_id=plugin_id, version='2.0.0', manifest_sha='2' * 40,
            manifest_snapshot={'version': '2.0.0'},
            synced_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
            is_current=True,
        )
        v3 = PluginVersion(
            plugin_id=plugin_id, version='3.0.0', manifest_sha='3' * 40,
            manifest_snapshot={'version': '3.0.0'},
            synced_at=datetime(2024, 1, 3, tzinfo=timezone.utc),
            is_current=False,
        )
        db.session.add_all([v1, v2, v3])
        db.session.commit()

        result = plugin_service.get_plugin_versions(plugin_id)

        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0]['version'] == '3.0.0'
        assert result[1]['version'] == '2.0.0'
        assert result[2]['version'] == '1.0.0'
        # 每个元素是 to_dict() 的形状
        assert set(result[0].keys()) >= {
            'id', 'plugin_id', 'version', 'manifest_sha',
            'manifest_snapshot', 'github_data_snapshot', 'synced_at', 'is_current',
        }
        assert result[0]['plugin_id'] == plugin_id

    def test_no_history_returns_empty_list(self, app, sample_plugin):
        """插件存在但无版本历史 -> 返回 []。"""
        result = plugin_service.get_plugin_versions(sample_plugin.id)
        assert result == []

    def test_missing_plugin_returns_empty_list(self, app):
        """插件不存在 -> 返回 []。"""
        result = plugin_service.get_plugin_versions(99999)
        assert result == []
