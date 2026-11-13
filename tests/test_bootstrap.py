from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import bootstrap
import export_cloned_paths
import pytest


def test_load_catalog_real_inventory() -> None:
    entries = bootstrap.load_catalog()
    assert len(entries) == 44
    kinds = [entry["kind"] for entry in entries]
    assert kinds.count("cli") == 13
    assert kinds.count("repo") == 30
    assert kinds.count("url") == 1


def test_scan_verify_report_matrix(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(bootstrap, "STATE_DIR", tmp_path / ".bootstrap")
    monkeypatch.setattr(
        bootstrap, "STATE_PATH", tmp_path / ".bootstrap" / "status.json"
    )
    monkeypatch.setattr(
        bootstrap, "REPORT_PATH", tmp_path / ".bootstrap" / "latest_report.md"
    )
    monkeypatch.setattr(bootstrap, "TOOLS_CACHE_DIR", tmp_path / ".tools-cache")

    repo_dir = tmp_path / ".tools-cache" / "demo-repo"
    repo_dir.mkdir(parents=True)
    (repo_dir / "README.md").write_text("# Demo Repo\n", encoding="utf-8")

    entries: list[dict[str, Any]] = [
        {
            "id": "gh-cli",
            "name": "gh",
            "kind": "cli",
            "binary": "gh",
            "verify": ["gh", "--version"],
        },
        {
            "id": "missing-cli",
            "name": "missing",
            "kind": "cli",
            "binary": "missing_bin_xyz",
        },
        {
            "id": "demo-repo",
            "name": "org/demo-repo",
            "kind": "repo",
            "cache_dir": "demo-repo",
        },
        {
            "id": "docs-url",
            "name": "skills.sh",
            "kind": "url",
            "verify": ["curl", "-IsS", "https://skills.sh"],
        },
    ]

    monkeypatch.setattr(
        bootstrap,
        "detect_cli",
        lambda entry: (
            (True, "binary found in PATH: gh")
            if entry["id"] == "gh-cli"
            else (False, "not detected")
        ),
    )
    monkeypatch.setattr(
        bootstrap,
        "run_cmd",
        lambda cmd, timeout=30: (
            (True, "ok") if cmd[0] in {"gh", "curl"} else (False, "err")
        ),
    )

    state: dict[str, Any] = {"rows": {}}
    bootstrap.scan(entries, state)
    bootstrap.verify(entries, state)
    rendered = bootstrap.report(entries, state)

    assert "| gh | yes | already | no | yes | yes |" in rendered
    assert "| missing | yes | no | no | no | yes |" in rendered
    assert "| org/demo-repo | yes | no | already | yes | yes |" in rendered
    assert "| skills.sh | yes | no | no | yes | yes |" in rendered
    assert (tmp_path / ".bootstrap" / "latest_report.md").exists()
    saved = json.loads(
        (tmp_path / ".bootstrap" / "status.json").read_text(encoding="utf-8")
    )
    assert saved["rows"]["demo-repo"]["Verified?"] == "yes"


def test_export_cloned_paths_with_mocked_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fake_script = tmp_path / "scripts" / "export_cloned_paths.py"
    fake_script.parent.mkdir(parents=True)
    fake_script.write_text("# placeholder\n", encoding="utf-8")
    (tmp_path / ".tools-cache" / "repo-one").mkdir(parents=True)
    (tmp_path / ".tools-cache" / "repo-two").mkdir(parents=True)

    monkeypatch.setattr(export_cloned_paths, "__file__", str(fake_script))
    rc = export_cloned_paths.main()
    assert rc == 0

    out = capsys.readouterr().out
    assert "exported=2" in out
    md_text = (tmp_path / ".bootstrap" / "cloned_repo_paths.md").read_text(
        encoding="utf-8"
    )
    assert "repo-one" in md_text
    assert "repo-two" in md_text
