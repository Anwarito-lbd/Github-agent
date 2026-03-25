#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "config" / "tool_catalog.json"
STATE_DIR = ROOT / ".bootstrap"
STATE_PATH = STATE_DIR / "status.json"
REPORT_PATH = STATE_DIR / "latest_report.md"
TOOLS_CACHE_DIR = ROOT / ".tools-cache"

COLUMNS = [
    "Tool/Repo",
    "Relevant?",
    "Installed?",
    "Cloned?",
    "Verified?",
    "Used in plan?",
    "Notes",
]


def load_catalog() -> list[dict[str, Any]]:
    if not CATALOG_PATH.exists():
        raise FileNotFoundError(f"Catalog missing: {CATALOG_PATH}")
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    entries = data.get("entries", [])
    if not isinstance(entries, list):
        raise ValueError("Catalog format invalid: entries must be a list.")
    return entries


def load_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return {"rows": {}}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"rows": {}}


def save_state(state: dict[str, Any]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


def ensure_row(state: dict[str, Any], entry: dict[str, Any]) -> dict[str, str]:
    rows = state.setdefault("rows", {})
    row = rows.get(entry["id"])
    if row is None:
        row = {
            "Tool/Repo": entry["name"],
            "Relevant?": "yes",
            "Installed?": "no",
            "Cloned?": "no",
            "Verified?": "no",
            "Used in plan?": "yes",
            "Notes": "",
        }
        rows[entry["id"]] = row
    row["Tool/Repo"] = entry["name"]
    row["Relevant?"] = "yes" if entry.get("relevant", True) else "no"
    row["Used in plan?"] = "yes" if entry.get("used_in_plan", True) else "no"
    if "Notes" not in row:
        row["Notes"] = ""
    return row


def join_cmd(cmd: list[str]) -> str:
    return " ".join(shlex.quote(x) for x in cmd)


def run_cmd(cmd: list[str], timeout: int = 240) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            cmd,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as exc:
        return False, f"missing binary: {exc}"
    except subprocess.TimeoutExpired:
        return False, f"timeout after {timeout}s"
    if result.returncode == 0:
        merged = "\n".join(
            part for part in [result.stdout, result.stderr] if part
        ).strip()
        return True, merged
    stderr = (result.stderr or "").strip()
    stdout = (result.stdout or "").strip()
    message = stderr or stdout or f"exit code {result.returncode}"
    lines = [line.strip() for line in message.splitlines() if line.strip()]
    if not lines:
        return False, message
    if len(lines) == 1:
        return False, lines[0]
    return False, f"{lines[0]} {lines[1]}"


def detect_cli(entry: dict[str, Any]) -> tuple[bool, str]:
    local_bin = entry.get("local_bin")
    if local_bin and (ROOT / local_bin).exists():
        return True, f"local binary found: {local_bin}"

    detect_cmd = entry.get("detect")
    if isinstance(detect_cmd, list) and detect_cmd:
        ok, msg = run_cmd(detect_cmd, timeout=30)
        if ok:
            required = entry.get("detect_contains")
            if required and required not in msg:
                return False, f"detect output mismatch for {join_cmd(detect_cmd)}"
            return True, f"detect passed: {join_cmd(detect_cmd)}"
        return False, f"detect failed: {msg}"

    binary = entry.get("binary")
    if binary and shutil.which(binary):
        return True, f"binary found in PATH: {binary}"

    return False, "not detected"


def append_note(row: dict[str, str], message: str) -> None:
    message = message.strip()
    if not message:
        return
    existing = row.get("Notes", "").strip()
    if not existing:
        row["Notes"] = message
    elif message not in existing:
        row["Notes"] = f"{existing}; {message}"


def ensure_npm_manifest() -> None:
    package_json = ROOT / "package.json"
    if package_json.exists():
        return
    package_json.write_text(
        json.dumps(
            {
                "name": "github-agent-bootstrap",
                "private": True,
                "version": "0.1.0",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def scan(entries: list[dict[str, Any]], state: dict[str, Any]) -> None:
    for entry in entries:
        row = ensure_row(state, entry)
        row["Verified?"] = "no"
        row["Notes"] = ""
        kind = entry.get("kind")

        if kind == "cli":
            found, detail = detect_cli(entry)
            row["Installed?"] = "already" if found else "no"
            row["Cloned?"] = "no"
            append_note(row, detail)
        elif kind == "repo":
            target = TOOLS_CACHE_DIR / entry["cache_dir"]
            row["Installed?"] = "no"
            row["Cloned?"] = "already" if target.exists() else "no"
            append_note(row, f"clone target: {target}")
        elif kind == "url":
            row["Installed?"] = "no"
            row["Cloned?"] = "no"
            append_note(row, "URL resource: install and clone not applicable")
        else:
            row["Installed?"] = "no"
            row["Cloned?"] = "no"
            append_note(row, f"unknown kind: {kind}")

    save_state(state)


def install(entries: list[dict[str, Any]], state: dict[str, Any]) -> None:
    for entry in entries:
        if entry.get("kind") != "cli":
            continue

        row = ensure_row(state, entry)
        if row["Relevant?"] != "yes":
            append_note(row, "skipped: not relevant")
            continue
        if row["Installed?"] in {"already", "yes"}:
            append_note(row, "install skipped: already installed")
            continue

        install_cmd = entry.get("install")
        if not isinstance(install_cmd, list) or not install_cmd:
            append_note(row, "install skipped: no install command")
            continue

        if install_cmd[:2] == ["npm", "install"]:
            ensure_npm_manifest()

        ok, msg = run_cmd(install_cmd, timeout=60)
        if ok:
            found, detail = detect_cli(entry)
            if found:
                row["Installed?"] = "yes"
                append_note(row, f"installed via: {join_cmd(install_cmd)}")
                append_note(row, detail)
            else:
                row["Installed?"] = "no"
                append_note(row, "install command ran but detection still failed")
        else:
            row["Installed?"] = "no"
            append_note(row, f"blocked: {msg}")
            manual = entry.get("manual_install")
            if manual:
                append_note(row, f"manual install: {manual}")

    save_state(state)


def clone(entries: list[dict[str, Any]], state: dict[str, Any]) -> None:
    TOOLS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    for entry in entries:
        if entry.get("kind") != "repo":
            continue

        row = ensure_row(state, entry)
        if row["Relevant?"] != "yes":
            append_note(row, "skipped: not relevant")
            continue
        if row["Cloned?"] in {"already", "yes"}:
            append_note(row, "clone skipped: already cloned")
            continue

        target = TOOLS_CACHE_DIR / entry["cache_dir"]
        clone_cmd = ["git", "clone", "--depth", "1", entry["repo_url"], str(target)]
        ok, msg = run_cmd(clone_cmd, timeout=60)
        if ok and target.exists():
            row["Cloned?"] = "yes"
            append_note(row, f"cloned into: {target}")
        else:
            row["Cloned?"] = "no"
            append_note(row, f"blocked: {msg}")
            append_note(row, f"manual clone: {join_cmd(clone_cmd)}")

    save_state(state)


def verify(entries: list[dict[str, Any]], state: dict[str, Any]) -> None:
    for entry in entries:
        row = ensure_row(state, entry)
        if row["Relevant?"] != "yes":
            row["Verified?"] = "no"
            append_note(row, "verify skipped: not relevant")
            continue

        kind = entry.get("kind")
        if kind == "cli":
            if row["Installed?"] == "no":
                row["Verified?"] = "no"
                append_note(row, "verify skipped: cli not installed")
                continue
            verify_cmd = entry.get("verify") or [entry.get("binary", ""), "--version"]
            if not verify_cmd or not verify_cmd[0]:
                row["Verified?"] = "no"
                append_note(row, "verify failed: no verify command")
                continue
            ok, msg = run_cmd(verify_cmd, timeout=180)
            if ok:
                required = entry.get("verify_contains")
                if required and required not in msg:
                    row["Verified?"] = "no"
                    append_note(row, f"verify failed: output missing '{required}'")
                else:
                    row["Verified?"] = "yes"
                    append_note(row, f"verify passed: {join_cmd(verify_cmd)}")
            else:
                row["Verified?"] = "no"
                append_note(row, f"verify failed: {msg}")
        elif kind == "repo":
            target = TOOLS_CACHE_DIR / entry["cache_dir"]
            if not target.exists():
                row["Verified?"] = "no"
                append_note(row, "verify skipped: repo not cloned")
                continue
            readmes = list(target.glob("README*"))
            row["Verified?"] = "yes" if readmes else "no"
            if readmes:
                append_note(row, f"verify passed: README present in {target.name}")
            else:
                append_note(row, f"verify failed: README missing in {target.name}")
        elif kind == "url":
            verify_cmd = entry.get("verify")
            if not verify_cmd:
                row["Verified?"] = "no"
                append_note(row, "verify skipped: no URL check command")
                continue
            ok, msg = run_cmd(verify_cmd, timeout=30)
            row["Verified?"] = "yes" if ok else "no"
            if ok:
                append_note(row, f"verify passed: {join_cmd(verify_cmd)}")
            else:
                append_note(row, f"verify failed: {msg}")
        else:
            row["Verified?"] = "no"
            append_note(row, f"verify skipped: unknown kind {kind}")

    save_state(state)


def report(entries: list[dict[str, Any]], state: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("| " + " | ".join(COLUMNS) + " |")
    lines.append("| " + " | ".join(["---"] * len(COLUMNS)) + " |")

    for entry in entries:
        row = ensure_row(state, entry)
        cells = []
        for col in COLUMNS:
            value = str(row.get(col, ""))
            value = value.replace("\n", " ").replace("|", "/")
            cells.append(value)
        lines.append("| " + " | ".join(cells) + " |")

    rendered = "\n".join(lines)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return rendered


def doctor() -> int:
    checks: list[tuple[list[str], str | None]] = [
        (["python3", "--version"], None),
        (["git", "--version"], None),
        (["task", "--help"], "Runs the specified task(s)."),
        (["mise", "--version"], None),
        (["uv", "--version"], None),
        (["ruff", "--version"], None),
        (["lefthook", "version"], None),
        (["node", "--version"], None),
        (["npm", "--version"], None),
    ]
    failures = 0
    for cmd, required in checks:
        ok, msg = run_cmd(cmd, timeout=20)
        if ok and required and required not in msg:
            ok = False
            msg = f"output missing '{required}'"
        prefix = "OK" if ok else "FAIL"
        print(f"{prefix:4} {join_cmd(cmd)} :: {msg}")
        if not ok:
            failures += 1
    return 0 if failures == 0 else 1


def run_all(entries: list[dict[str, Any]], state: dict[str, Any]) -> None:
    scan(entries, state)
    install(entries, state)
    clone(entries, state)
    verify(entries, state)
    report(entries, state)


def main() -> int:
    parser = argparse.ArgumentParser(description="Toolchain bootstrap runner")
    parser.add_argument(
        "command",
        choices=["scan", "install", "clone", "verify", "report", "all", "doctor"],
        help="Subcommand to execute",
    )
    args = parser.parse_args()

    if args.command == "doctor":
        return doctor()

    entries = load_catalog()
    state = load_state()

    if args.command == "scan":
        scan(entries, state)
        return 0
    if args.command == "install":
        install(entries, state)
        return 0
    if args.command == "clone":
        clone(entries, state)
        return 0
    if args.command == "verify":
        verify(entries, state)
        return 0
    if args.command == "report":
        report(entries, state)
        return 0
    if args.command == "all":
        run_all(entries, state)
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
