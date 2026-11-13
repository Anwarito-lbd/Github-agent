from __future__ import annotations

import base64
import importlib.util
import json
import stat
import subprocess
import zipfile
from pathlib import Path
from typing import Any

import pytest
import requests

ROOT = Path(__file__).resolve().parents[1]


def load_collector_module() -> Any:
    spec = importlib.util.spec_from_file_location(
        "github_agent", ROOT / "github.agent.py"
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


agent = load_collector_module()


class FakeResponse:
    def __init__(
        self,
        status_code: int,
        payload: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status_code = status_code
        self._payload = payload or {}
        self.headers = headers or {}

    def json(self) -> dict[str, Any]:
        return self._payload


class FakeSession:
    def __init__(self, responses: list[FakeResponse | Exception]) -> None:
        self._responses = list(responses)
        self.calls: list[dict[str, Any]] = []
        self.closed = False

    def get(
        self,
        url: str,
        *,
        headers: dict[str, str],
        params: dict[str, Any],
        timeout: int,
    ) -> FakeResponse:
        self.calls.append(
            {
                "url": url,
                "headers": headers,
                "params": params,
                "timeout": timeout,
            }
        )
        item = self._responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    def close(self) -> None:
        self.closed = True


def make_api_item(
    name: str,
    owner: str,
    stars: int,
    language: str = "Python",
) -> dict[str, Any]:
    full_name = f"{owner}/{name}"
    return {
        "name": name,
        "full_name": full_name,
        "clone_url": f"https://github.com/{full_name}.git",
        "html_url": f"https://github.com/{full_name}",
        "stargazers_count": stars,
        "owner": {"login": owner},
        "language": language,
        "description": f"{name} description",
    }


def make_normalized_repo(
    name: str,
    owner: str,
    stars: int,
    language: str = "Python",
) -> dict[str, Any]:
    full_name = f"{owner}/{name}"
    return {
        "name": name,
        "full_name": full_name,
        "clone_url": f"https://github.com/{full_name}.git",
        "html_url": f"https://github.com/{full_name}",
        "stars": stars,
        "owner": owner,
        "language": language,
        "description": f"{name} description",
    }


def test_clean_filename_and_search_query() -> None:
    assert agent.clean_filename("portfolio react") == "portfolio_react"
    assert agent.clean_filename("django/ecommerce") == "django_ecommerce"
    assert agent.clean_filename("a b*c?") == "a_b_c_"
    assert agent.clean_filename("ok_name-1") == "ok_name-1"

    assert (
        agent.build_search_query("trading bot", language="python", min_stars=100)
        == "trading bot language:python stars:>=100"
    )
    assert (
        agent.build_search_query(
            "trading language:rust stars:>50", language="python", min_stars=100
        )
        == "trading language:rust stars:>50"
    )


def test_resolve_token_precedence(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "env-gh-val")
    monkeypatch.setenv("GH_TOKEN", "env-cli-val")
    assert agent.resolve_token("explicit-val") == "explicit-val"
    assert agent.resolve_token(None) == "env-gh-val"

    monkeypatch.delenv("GITHUB_TOKEN")
    assert agent.resolve_token(None) == "env-cli-val"

    monkeypatch.delenv("GH_TOKEN")
    assert agent.resolve_token(None) == ""


def test_build_git_auth_env_never_exposes_token_in_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("GIT_CONFIG_COUNT", raising=False)
    sample_val = "ghp_example_12345"
    env = agent.build_git_auth_env(sample_val)

    assert env["GIT_TERMINAL_PROMPT"] == "0"
    assert env["GIT_CONFIG_COUNT"] == "1"
    assert env["GIT_CONFIG_KEY_0"] == "http.https://github.com/.extraheader"
    expected_b64 = base64.b64encode(f"x-access-token:{sample_val}".encode()).decode(
        "ascii"
    )
    assert env["GIT_CONFIG_VALUE_0"] == f"AUTHORIZATION: basic {expected_b64}"

    anon_env = agent.build_git_auth_env("")
    assert anon_env["GIT_TERMINAL_PROMPT"] == "0"
    assert "GIT_CONFIG_COUNT" not in anon_env


def test_search_github_pagination_dedup_and_per_page() -> None:
    # Page 1 returns 3 items (matching per_page=3), with one duplicate so 2 unique are kept
    # Page 2 fetches the remaining 1 item (per_page=1) to satisfy limit=3.
    page1 = FakeResponse(
        200,
        {
            "total_count": 250,
            "items": [
                make_api_item("repo-a", "alice", 500),
                make_api_item("repo-b", "bob", 300),
                make_api_item("repo-b", "bob", 300),
            ],
        },
    )
    page2 = FakeResponse(
        200,
        {
            "total_count": 250,
            "items": [
                make_api_item("repo-c", "carol", 400),
            ],
        },
    )
    session = FakeSession([page1, page2])

    results = agent.search_github(
        "portfolio", 3, "tok_abc", session=session, retry_backoff=0.0
    )

    assert [r["full_name"] for r in results] == [
        "alice/repo-a",
        "carol/repo-c",
        "bob/repo-b",
    ]
    assert len(session.calls) == 2
    assert session.calls[0]["params"]["per_page"] == 3
    assert session.calls[1]["params"]["per_page"] == 1
    assert session.calls[0]["headers"]["Authorization"] == "Bearer tok_abc"
    assert (
        session.calls[0]["headers"]["X-GitHub-Api-Version"] == agent.GITHUB_API_VERSION
    )


def test_search_github_handles_401_403_422_and_500() -> None:
    s_401 = FakeSession([FakeResponse(401)])
    assert (
        agent.search_github("portfolio", 5, "bad", session=s_401, retry_backoff=0.0)
        == []
    )

    s_422 = FakeSession([FakeResponse(422)])
    assert agent.search_github("bad:::", 5, "", session=s_422, retry_backoff=0.0) == []

    s_403 = FakeSession(
        [
            FakeResponse(
                200, {"total_count": 100, "items": [make_api_item("one", "u1", 99)]}
            ),
            FakeResponse(
                403,
                headers={
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": "1794540000",
                },
            ),
        ]
    )
    partial = agent.search_github("portfolio", 5, "", session=s_403, retry_backoff=0.0)
    assert [r["full_name"] for r in partial] == ["u1/one"]

    s_500 = FakeSession(
        [
            FakeResponse(502),
            FakeResponse(
                200, {"total_count": 1, "items": [make_api_item("ok", "u2", 50)]}
            ),
        ]
    )
    recovered = agent.search_github(
        "portfolio", 1, "", session=s_500, retry_backoff=0.0
    )
    assert [r["full_name"] for r in recovered] == ["u2/ok"]

    s_err = FakeSession([requests.ConnectionError("dns failed")])
    assert (
        agent.search_github("portfolio", 3, "", session=s_err, retry_backoff=0.0) == []
    )
    assert (
        agent.search_github("portfolio", 0, "", session=s_err, retry_backoff=0.0) == []
    )


def test_clone_single_repo_strips_git_and_avoids_token_in_args(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recorded: dict[str, Any] = {}

    def fake_run(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        recorded["cmd"] = cmd
        recorded["env"] = kwargs["env"]
        target = Path(cmd[-1])
        git_dir = target / ".git"
        git_dir.mkdir(parents=True)
        pack_file = git_dir / "pack.idx"
        pack_file.write_text("pack", encoding="utf-8")
        pack_file.chmod(stat.S_IREAD)
        (target / "README.md").write_text("# Demo", encoding="utf-8")
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(agent.subprocess, "run", fake_run)

    repo = make_normalized_repo("quantstats", "ranaroussi", 7861)
    secret_val = "ghp_super_secret"
    cloned = agent.clone_single_repo(repo, secret_val, work_dir=tmp_path)

    assert cloned == repo
    assert secret_val not in " ".join(recorded["cmd"])
    assert recorded["cmd"][:3] == ["git", "clone", "--depth"]
    assert recorded["env"]["GIT_CONFIG_COUNT"] == "1"
    target_dir = tmp_path / "quantstats_ranaroussi"
    assert (target_dir / "README.md").exists()
    assert not (target_dir / ".git").exists()


def test_clone_single_repo_cleans_up_on_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def failing_run(
        cmd: list[str], **_kwargs: Any
    ) -> subprocess.CompletedProcess[bytes]:
        target = Path(cmd[-1])
        target.mkdir(parents=True, exist_ok=True)
        (target / "partial.txt").write_text("partial", encoding="utf-8")
        raise subprocess.CalledProcessError(128, cmd)

    monkeypatch.setattr(agent.subprocess, "run", failing_run)

    repo = make_normalized_repo("broken", "org", 10)
    assert agent.clone_single_repo(repo, "", work_dir=tmp_path) is None
    assert not (tmp_path / "broken_org").exists()


def test_package_repos_creates_zip_with_report(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_clone(
        repo: dict[str, Any],
        _token: str,
        *,
        work_dir: Path | None = None,
        timeout: int = 180,
    ) -> dict[str, Any]:
        assert work_dir is not None
        assert timeout > 0
        folder = work_dir / agent.clean_filename(f"{repo['name']}_{repo['owner']}")
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "app.py").write_text("print('ok')\n", encoding="utf-8")
        return repo

    monkeypatch.setattr(agent, "clone_single_repo", fake_clone)
    repos = [
        make_normalized_repo("alpha", "dev1", 120),
        make_normalized_repo("beta", "dev2", 80),
    ]
    count, archive = agent.package_repos(
        repos,
        query="alpha beta",
        limit=2,
        token="",
        base_dir=tmp_path,
        work_dir=tmp_path / "temp_repos",
        workers=2,
    )

    assert count == 2
    assert archive.exists()
    assert not (tmp_path / "temp_repos").exists()
    with zipfile.ZipFile(archive) as zf:
        names = set(zf.namelist())
        assert "_RAPPORT_DE_RECHERCHE.txt" in names
        assert "alpha_dev1/app.py" in names
        assert "beta_dev2/app.py" in names


def test_cli_dry_run_json_and_empty_query(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    sample = [make_normalized_repo("quantstats", "ranaroussi", 7861)]
    monkeypatch.setattr(agent, "search_github", lambda q, lim, tok: sample)

    rc = agent.main(["--query", "quant", "--limit", "1", "--dry-run", "--json"])
    assert rc == 0
    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert parsed[0]["full_name"] == "ranaroussi/quantstats"

    with pytest.raises(SystemExit) as exc_info:
        agent.main(["--query", "   ", "--dry-run"])
    assert exc_info.value.code == 1
