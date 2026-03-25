#!/usr/bin/env python3

from __future__ import annotations

import os
import socket
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def resolve(host: str) -> bool:
    try:
        socket.gethostbyname(host)
        return True
    except OSError:
        return False


def main() -> int:
    pip_cache = ROOT / ".cache" / "pip"
    npm_cache = ROOT / ".cache" / "npm"
    pip_cache.mkdir(parents=True, exist_ok=True)
    npm_cache.mkdir(parents=True, exist_ok=True)

    cellar = Path("/opt/homebrew/Cellar")
    if not os.access(cellar, os.W_OK):
        print(
            "WARN brew cellar not writable. If needed, run: "
            "sudo chown -R $(whoami):admin /opt/homebrew/Cellar"
        )

    for host in ["github.com", "skills.sh", "registry.npmjs.org", "pypi.org"]:
        if not resolve(host):
            print(f"WARN cannot resolve host: {host}")

    env = os.environ.copy()
    env["PIP_CACHE_DIR"] = str(pip_cache)
    env["NPM_CONFIG_CACHE"] = str(npm_cache)

    cmd = ["python3", "scripts/bootstrap.py", "all"]
    print(f"RUN {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=ROOT, env=env, check=False)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
