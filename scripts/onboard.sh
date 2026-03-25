#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[onboard] repo: $ROOT_DIR"

if ! command -v task >/dev/null 2>&1; then
  echo "[onboard] task missing. Installing go-task with Homebrew..."
  if command -v brew >/dev/null 2>&1; then
    brew install go-task
  else
    echo "[onboard] brew not found. Install go-task manually: brew install go-task"
  fi
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "[onboard] uv missing. Installing with Homebrew..."
  if command -v brew >/dev/null 2>&1; then
    brew install uv
  else
    echo "[onboard] brew not found. Install uv manually: brew install uv"
  fi
fi

if command -v uv >/dev/null 2>&1; then
  echo "[onboard] running setup"
  uv venv
  uv pip install -r requirements.txt
fi

echo "[onboard] running bootstrap retry"
python3 scripts/bootstrap_retry.py

echo "[onboard] done. Report: .bootstrap/latest_report.md"
