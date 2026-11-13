# Proof of work

Commands below were run from the repository root on 13 November 2026. Outputs are copied from that run. No GitHub token was provided. No catalog repository was cloned, and the three search hits were not cloned either.

Host facts observed during the run:

| Check | Result |
| --- | --- |
| `python3 --version` | Python 3.12.3 |
| `git --version` | git version 2.43.0 |
| `node --version` | v22.23.4 |
| `npm --version` | 10.9.9 |
| `gh --version` | gh version 2.103.0 (2026-10-21) |
| `go version` | go version go1.22.2 linux/amd64 |
| `command -v` task, mise, uv, ruff, lefthook, brew | missing |
| `.mise.toml` pins | python 3.13, node 24 (mise itself was not installed) |

## Compile and shell syntax

```text
python3 -m py_compile github.agent.py scripts/bootstrap.py scripts/bootstrap_retry.py scripts/export_cloned_paths.py
bash -n scripts/onboard.sh
```

Both commands exited 0 and printed nothing.

## Doctor

```text
python3 scripts/bootstrap.py doctor
```

Exit code 1.

```text
OK   python3 --version :: Python 3.12.3
OK   git --version :: git version 2.43.0
FAIL task --help :: missing binary: [Errno 2] No such file or directory: 'task'
FAIL mise --version :: missing binary: [Errno 2] No such file or directory: 'mise'
FAIL uv --version :: missing binary: [Errno 2] No such file or directory: 'uv'
FAIL ruff --version :: missing binary: [Errno 2] No such file or directory: 'ruff'
FAIL lefthook version :: missing binary: [Errno 2] No such file or directory: 'lefthook'
OK   node --version :: v22.23.4
OK   npm --version :: 10.9.9
```

## Scan, verify, report

```text
python3 scripts/bootstrap.py scan
python3 scripts/bootstrap.py verify
python3 scripts/bootstrap.py report
```

Scan and verify printed nothing and exited 0. Report exited 0 and printed the table below. The same bytes were written to `.bootstrap/latest_report.md`, which is gitignored.

Counts from this table: 44 rows, 1 verified CLI (`gh`), 1 verified URL (`skills.sh`), 12 CLIs not installed, 30 repositories not cloned.

| Tool/Repo | Relevant? | Installed? | Cloned? | Verified? | Used in plan? | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| gh | yes | already | no | yes | yes | binary found in PATH: gh; verify passed: gh --version |
| task | yes | no | no | no | yes | detect failed: missing binary: [Errno 2] No such file or directory: 'task'; verify skipped: cli not installed |
| mise | yes | no | no | no | yes | not detected; verify skipped: cli not installed |
| lefthook | yes | no | no | no | yes | not detected; verify skipped: cli not installed |
| uv | yes | no | no | no | yes | not detected; verify skipped: cli not installed |
| ruff | yes | no | no | no | yes | not detected; verify skipped: cli not installed |
| biome | yes | no | no | no | yes | not detected; verify skipped: cli not installed |
| nx | yes | no | no | no | yes | not detected; verify skipped: cli not installed |
| supabase | yes | no | no | no | yes | not detected; verify skipped: cli not installed |
| vercel | yes | no | no | no | yes | not detected; verify skipped: cli not installed |
| stripe | yes | no | no | no | yes | not detected; verify skipped: cli not installed |
| playwright-cli | yes | no | no | no | yes | detect failed: github-agent-bootstrap@0.1.0 /workspace └── (empty); verify skipped: cli not installed |
| notebooklm-py | yes | no | no | no | yes | detect failed: WARNING: Package(s) not found: notebooklm-py; verify skipped: cli not installed |
| skills.sh | yes | no | no | yes | yes | URL resource: install and clone not applicable; verify passed: curl -IsS --max-time 10 https://skills.sh |
| VoltAgent/awesome-claude-code-subagents | yes | no | no | no | yes | clone target: /workspace/.tools-cache/awesome-claude-code-subagents; verify skipped: repo not cloned |
| thedotmack/claude-mem | yes | no | no | no | yes | clone target: /workspace/.tools-cache/claude-mem; verify skipped: repo not cloned |
| vercel-labs/skills | yes | no | no | no | yes | clone target: /workspace/.tools-cache/vercel-labs-skills; verify skipped: repo not cloned |
| kcchien/skills-cli | yes | no | no | no | yes | clone target: /workspace/.tools-cache/skills-cli; verify skipped: repo not cloned |
| automazeio/ccpm | yes | no | no | no | yes | clone target: /workspace/.tools-cache/ccpm; verify skipped: repo not cloned |
| modelcontextprotocol/servers | yes | no | no | no | yes | clone target: /workspace/.tools-cache/mcp-servers; verify skipped: repo not cloned |
| shanraisshan/claude-code-hooks | yes | no | no | no | yes | clone target: /workspace/.tools-cache/claude-code-hooks; verify skipped: repo not cloned |
| shanraisshan/claude-code-best-practice | yes | no | no | no | yes | clone target: /workspace/.tools-cache/claude-code-best-practice; verify skipped: repo not cloned |
| affaan-m/everything-claude-code | yes | no | no | no | yes | clone target: /workspace/.tools-cache/everything-claude-code; verify skipped: repo not cloned |
| obra/superpowers | yes | no | no | no | yes | clone target: /workspace/.tools-cache/superpowers; verify skipped: repo not cloned |
| gsd-build/get-shit-done | yes | no | no | no | yes | clone target: /workspace/.tools-cache/get-shit-done; verify skipped: repo not cloned |
| github/spec-kit | yes | no | no | no | yes | clone target: /workspace/.tools-cache/spec-kit; verify skipped: repo not cloned |
| AgriciDaniel/claude-ads | yes | no | no | no | yes | clone target: /workspace/.tools-cache/claude-ads; verify skipped: repo not cloned |
| go-task/task | yes | no | no | no | yes | clone target: /workspace/.tools-cache/go-task-task; verify skipped: repo not cloned |
| jdx/mise | yes | no | no | no | yes | clone target: /workspace/.tools-cache/jdx-mise; verify skipped: repo not cloned |
| evilmartians/lefthook | yes | no | no | no | yes | clone target: /workspace/.tools-cache/lefthook; verify skipped: repo not cloned |
| astral-sh/uv | yes | no | no | no | yes | clone target: /workspace/.tools-cache/astral-uv; verify skipped: repo not cloned |
| astral-sh/ruff | yes | no | no | no | yes | clone target: /workspace/.tools-cache/astral-ruff; verify skipped: repo not cloned |
| biomejs/biome | yes | no | no | no | yes | clone target: /workspace/.tools-cache/biome; verify skipped: repo not cloned |
| nrwl/nx | yes | no | no | no | yes | clone target: /workspace/.tools-cache/nx; verify skipped: repo not cloned |
| supabase/cli | yes | no | no | no | yes | clone target: /workspace/.tools-cache/supabase-cli; verify skipped: repo not cloned |
| stripe/stripe-cli | yes | no | no | no | yes | clone target: /workspace/.tools-cache/stripe-cli; verify skipped: repo not cloned |
| googleworkspace/cli | yes | no | no | no | yes | clone target: /workspace/.tools-cache/googleworkspace-cli; verify skipped: repo not cloned |
| HKUDS/CLI-Anything | yes | no | no | no | yes | clone target: /workspace/.tools-cache/cli-anything; verify skipped: repo not cloned |
| microsoft/playwright-cli | yes | no | no | no | yes | clone target: /workspace/.tools-cache/playwright-cli; verify skipped: repo not cloned |
| teng-lin/notebooklm-py | yes | no | no | no | yes | clone target: /workspace/.tools-cache/notebooklm-py; verify skipped: repo not cloned |
| astral-sh/setup-uv | yes | no | no | no | yes | clone target: /workspace/.tools-cache/setup-uv; verify skipped: repo not cloned |
| astral-sh/ruff-action | yes | no | no | no | yes | clone target: /workspace/.tools-cache/ruff-action; verify skipped: repo not cloned |
| go-task/setup-task | yes | no | no | no | yes | clone target: /workspace/.tools-cache/setup-task; verify skipped: repo not cloned |
| jdx/mise-action | yes | no | no | no | yes | clone target: /workspace/.tools-cache/mise-action; verify skipped: repo not cloned |

`gh --version` on its own printed:

```text
gh version 2.103.0 (2026-10-21)
https://github.com/cli/cli/releases/tag/v2.103.0
```

`curl -IsS --max-time 10 https://skills.sh` returned a redirect. The status line and location header were:

```text
HTTP/2 308
location: https://www.skills.sh/
date: Fri, 13 Nov 2026 02:03:47 GMT
```

## Cloned-path export

```text
python3 scripts/export_cloned_paths.py
```

Exit code 0.

```text
exported=0
txt=/workspace/.bootstrap/cloned_repo_paths.txt
md=/workspace/.bootstrap/cloned_repo_paths.md
```

## Collector: empty query

`requests` and `tqdm` were not installed on the system Python. They were installed from `requirements.txt` into `/tmp/ga-pydeps` and exposed with `PYTHONPATH`. `pip show` reported `requests` 2.34.2 and `tqdm` 4.70.1.

```text
printf '\n\n' | PYTHONPATH=/tmp/ga-pydeps python3 github.agent.py
```

Exit code 1.

```text

============================================================
      🤖 GITHUB AUTO-COLLECTOR AGENT
      Recherche -> Clone -> Zip
============================================================

📝 VEUILLEZ RÉPONDRE AUX QUESTIONS :

1. Collez votre Token GitHub (Classic) pour l'accès API.
   (Si vous n'en avez pas, appuyez juste sur Entrée, mais la recherche sera limitée)
   👉 Token : 
2. Que cherchez-vous ? (ex: 'trading bot python', 'portfolio react', 'django ecommerce')
   👉 Recherche : ❌ Vous devez écrire quelque chose !
```

The error sits on the prompt line because stdin was a pipe: the newline that ended the empty query was not echoed.

## Collector: helpers and search, no clone

The module filename is `github.agent.py`, so it was loaded with `importlib` from that path. `search_github` was called with an empty token. `clone_single_repo` was not called.

```text
git_installed True
clean_filename 'portfolio react' -> 'portfolio_react'
clean_filename 'django/ecommerce' -> 'django_ecommerce'
clean_filename 'a b*c?' -> 'a_b_c_'
clean_filename 'ok_name-1' -> 'ok_name-1'

🔎 Recherche des 3 meilleurs dépôts pour : 'portfolio language:python'...
search_count 3
27679	emmabostian/developer-portfolios	https://github.com/emmabostian/developer-portfolios.git
7861	ranaroussi/quantstats	https://github.com/ranaroussi/quantstats.git
7551	LuckyOne7777/LLM-Trading-Lab	https://github.com/LuckyOne7777/LLM-Trading-Lab.git
```

Exit code 0.

## Ruff

Ruff was not on `PATH`. `python3 -m pip install --prefix /tmp/ruff-prefix ruff` installed ruff 0.17.5. The binary was `/tmp/ruff-prefix/local/bin/ruff`.

```text
ruff 0.17.5
```

`ruff check` on `github.agent.py`, `scripts/bootstrap.py`, `scripts/bootstrap_retry.py`, and `scripts/export_cloned_paths.py` exited 1:

```text
Found 14 errors.
[*] 5 fixable with `--fix`.
```

| Rule | Location |
| --- | --- |
| EXE001 | `github.agent.py:1` |
| UP009 | `github.agent.py:2` |
| I001 | `github.agent.py:15` |
| F401 | `github.agent.py:19` (`time` imported but unused) |
| PLW1510 | `github.agent.py:58` |
| BLE001 | `github.agent.py:124` |
| BLE001 | `github.agent.py:172` |
| FURB122 | `github.agent.py:252` |
| F541 | `github.agent.py:268` |
| BLE001 | `github.agent.py:277` |
| EXE001 | `scripts/bootstrap.py:1` |
| TRY004 | `scripts/bootstrap.py:38` |
| EXE001 | `scripts/bootstrap_retry.py:1` |
| EXE001 | `scripts/export_cloned_paths.py:1` |

`ruff format --check` on the same four files exited 1:

```text
1 file would be reformatted, 3 files already formatted
```

The file that would be reformatted is `github.agent.py`. The sources were not modified.

## DNS preflight from the retry script

`scripts/bootstrap_retry.py` was imported and its `resolve()` function was called. `main()` was not called, so `bootstrap.py all` did not run.

```text
brew_cellar_exists False
brew_cellar_writable False
resolve github.com True
resolve skills.sh True
resolve registry.npmjs.org True
resolve pypi.org True
resolve api.github.com True
```

`api.github.com` is not in the retry script's host list. It was resolved with the same function because the collector calls that host.

## Commands that were not run

| Command | Why it was skipped |
| --- | --- |
| `python3 scripts/bootstrap.py install` | Installs CLIs, mostly through Homebrew, which is not on this machine. npm and pip installs would also change the tree. |
| `python3 scripts/bootstrap.py clone` | Clones all 30 catalog repositories into `.tools-cache/`. |
| `python3 scripts/bootstrap.py all` | Scan plus install, clone, verify, and report. |
| `python3 scripts/bootstrap_retry.py` | Runs `bootstrap.py all` after the preflight. |
| `bash scripts/onboard.sh` | Runs uv setup and then the retry script. `uv` is not installed. |
| A full `python3 github.agent.py` session with a query | Would clone and zip the search results. |
| GitHub Actions `Bootstrap Checks` | Not executed from this environment. The workflow file is the source for what CI is configured to run. |

## Tests

A search of the tree found no test files and no `test` script in `package.json`.

## Follow-up: Bootstrap Checks failed on the same ruff findings

GitHub Actions run 43350160230, job `bootstrap-check`, conclusion failure. Checkout, Setup mise, Setup Task, and Setup uv succeeded. Setup ruff failed. Setup Go, Install lefthook, Bootstrap scan, and Doctor were skipped.

The failing step is `astral-sh/ruff-action@v3` with default `args: check`. The log says it installed ruff 0.17.5 and then ran:

```text
ruff check /home/runner/work/Github-agent/Github-agent
```

The annotations were the same 14 rules listed above (`EXE001`, `UP009`, `I001`, `F401`, `PLW1510`, `BLE001`, `FURB122`, `F541`, `TRY004`). The log line was:

```text
The process '/opt/hostedtoolcache/ruff/0.17.5/x86_64/ruff' failed with exit code 1
```

Run URL: https://github.com/Anwarito-lbd/Github-agent/actions/runs/43350160230

The follow-up commit fixes those findings and formats `github.agent.py`. Re-run on this machine with `/tmp/ruff-prefix/local/bin/ruff` 0.17.5:

```text
ruff check .
```

```text
All checks passed!
```

Exit code 0.

```text
ruff format --check github.agent.py scripts/bootstrap.py scripts/bootstrap_retry.py scripts/export_cloned_paths.py
```

```text
4 files already formatted
```

Exit code 0.

`python3 -m py_compile` on the four Python files exited 0. The empty-query stdin path still exited 1 with `Vous devez écrire quelque chose !`. `search_github("portfolio language:python", 3, "")` still returned three repositories and did not clone them. Star counts on that second call were 27679, 7862, and 7551 for the same three full names as the first call.

## Follow-up: lefthook did not compile on Go 1.27.4

GitHub Actions run 43350526650, job `bootstrap-check`, conclusion failure. Setup ruff succeeded. Install lefthook failed. Bootstrap scan and Doctor were skipped.

The step ran `go install github.com/evilmartians/lefthook@latest` after `actions/setup-go@v5` with `go-version: stable`, which resolved to go1.27.4. The module resolved to lefthook v1.13.6. The compiler errors were:

```text
# github.com/go-json-experiment/json
../../../go/pkg/mod/github.com/go-json-experiment/json@v0.0.0-20250910080747-cc2cfa0554c3/alias.go:618:21: undefined: json.SkipFunc
../../../go/pkg/mod/github.com/go-json-experiment/json@v0.0.0-20250910080747-cc2cfa0554c3/alias.go:980:14: undefined: json.DiscardUnknownMembers
Process completed with exit code 1.
```

Run URL: https://github.com/Anwarito-lbd/Github-agent/actions/runs/43350526650

The workflow now downloads the lefthook v2.2.2 release archive instead of compiling `@latest`. The asset checked on this x86_64 machine was `lefthook_2.2.2_Linux_x86_64.gz`. After gunzip, `lefthook version` printed:

```text
2.2.2
```

Exit code 0. The GitHub runner result for scan and doctor is in the section below.

## Follow-up: install had no destination directory

GitHub Actions run 43350887717 failed in Install lefthook after the download. The log line was:

```text
install: invalid target '/home/runner/.local/bin/lefthook': No such file or directory
Process completed with exit code 1.
```

Run URL: https://github.com/Anwarito-lbd/Github-agent/actions/runs/43350887717

The same `install` on this machine, pointed at a directory that does not exist, exits 1 with `install: cannot create regular file`. Creating the directory first, then installing the v2.2.2 binary, prints `2.2.2` and exits 0. The workflow now runs `mkdir -p "$HOME/.local/bin"` before `install`.

Task v3.54.0, the version that run installed, exits 0 for `task --help` and writes `Runs the specified task(s).` on stderr. `doctor` reads stdout and stderr together, so that substring is visible to it.

## Follow-up: Bootstrap Checks passed

GitHub Actions run 43351099399, job `bootstrap-check`, conclusion success, on commit `0819e82`. Every step succeeded: Checkout, Setup mise, Setup Task, Setup uv, Setup ruff, Install lefthook, Bootstrap scan, and Doctor.

Install lefthook printed `2.2.2`. Scan ran `python3 scripts/bootstrap.py scan` and printed nothing else. Doctor printed these lines, among the task help text that `task --help` writes to stderr:

```text
OK   python3 --version :: Python 3.13.18
OK   git --version :: git version 2.56.0
OK   mise --version :: 2026.11.7 linux-x64 (2026-11-12)
OK   uv --version :: uv 0.13.8 (x86_64-unknown-linux-gnu)
OK   ruff --version :: ruff 0.17.5
OK   lefthook version :: 2.2.2
OK   node --version :: v24.22.3
OK   npm --version :: 11.19.1
```

The `task --help` row was also `OK`. Its message is the full usage text, which includes `Runs the specified task(s).`

Run URL: https://github.com/Anwarito-lbd/Github-agent/actions/runs/43351099399

---

## Follow-up: Collector API hardening, non-interactive CLI, and pytest suite (Windows verification pass)

Verified on Windows 11 after adding non-interactive CLI flags (`--query`, `--limit`, `--language`, `--min-stars`, `--dry-run`, `--json`), `GIT_CONFIG_*` header auth, rate-limit diagnostics (`X-RateLimit-*` / `Retry-After` / `422` / `5xx` retry), cross-platform `.git` cleanup, Windows `.cmd` shim resolution in `scripts/bootstrap.py`, and 12 `pytest` unit tests (`tests/test_github_agent.py`, `tests/test_bootstrap.py`).

Host tool versions observed:

| Check | Result |
| --- | --- |
| `python --version` | Python 3.12.10 |
| `ruff --version` | ruff 0.16.8 |
| `pytest --version` | pytest 9.1.1 |
| `uv --version` | uv 0.12.3 |
| `gh --version` | gh version 2.96.0 (2026-07-02) |
| `git --version` | git version 2.55.0.windows.3 |
| `node --version` / `npm --version` | v24.19.0 / 11.17.0 |

### Compile, Ruff lint, Ruff format, and Pytest

```text
python -m py_compile github.agent.py scripts/bootstrap.py scripts/bootstrap_retry.py scripts/export_cloned_paths.py tests/test_github_agent.py tests/test_bootstrap.py
ruff check .
ruff check . --isolated
ruff format --check .
uv run --no-project --with-requirements requirements.txt --with pytest pytest -v
```

Outputs (all exited `0`):

```text
All checks passed!
All checks passed!
10 files already formatted
Installed 12 packages in 2.07s
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.2.0, pluggy-1.7.0 -- C:\Users\issao\AppData\Local\uv\cache\builds-v0\.tmpEqU42g\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\issao\Downloads\portfolio\agy-work\Github-agent
configfile: pyproject.toml
testpaths: tests
collecting ... collected 12 items

tests/test_bootstrap.py::test_load_catalog_real_inventory PASSED         [  8%]
tests/test_bootstrap.py::test_scan_verify_report_matrix PASSED           [ 16%]
tests/test_bootstrap.py::test_export_cloned_paths_with_mocked_root PASSED [ 25%]
tests/test_github_agent.py::test_clean_filename_and_search_query PASSED  [ 33%]
tests/test_github_agent.py::test_resolve_token_precedence PASSED         [ 41%]
tests/test_github_agent.py::test_build_git_auth_env_never_exposes_token_in_url PASSED [ 50%]
tests/test_github_agent.py::test_search_github_pagination_dedup_and_per_page PASSED [ 58%]
tests/test_github_agent.py::test_search_github_handles_401_403_422_and_500 PASSED [ 66%]
tests/test_github_agent.py::test_clone_single_repo_strips_git_and_avoids_token_in_args PASSED [ 75%]
tests/test_github_agent.py::test_clone_single_repo_cleans_up_on_failure PASSED [ 83%]
tests/test_github_agent.py::test_package_repos_creates_zip_with_report PASSED [ 91%]
tests/test_github_agent.py::test_cli_dry_run_json_and_empty_query PASSED [100%]

============================= 12 passed in 2.15s ==============================
```

### Live GitHub REST Search API CLI demos (`--dry-run` and `--dry-run --json`)

```text
python github.agent.py --query "portfolio" --language python --limit 3 --dry-run
```

Exit code `0`:

```text
============================================================
      🤖 GITHUB AUTO-COLLECTOR AGENT
      Recherche -> Clone -> Zip
============================================================


🔎 Recherche des 3 meilleurs dépôts pour : 'portfolio language:python'...

🧪 Mode dry-run (aucun clonage ni archive ZIP) :
  - [27679★] emmabostian/developer-portfolios [Python] -> https://github.com/emmabostian/developer-portfolios.git
  - [7862★] ranaroussi/quantstats [Python] -> https://github.com/ranaroussi/quantstats.git
  - [7552★] LuckyOne7777/LLM-Trading-Lab [Python] -> https://github.com/LuckyOne7777/LLM-Trading-Lab.git
```

```text
python github.agent.py --query "fastapi" --min-stars 1000 --limit 3 --dry-run --json
```

Exit code `0`:

```text
🔎 Recherche des 3 meilleurs dépôts pour : 'fastapi stars:>=1000'...
[
  {
    "name": "fastapi",
    "full_name": "fastapi/fastapi",
    "clone_url": "https://github.com/fastapi/fastapi.git",
    "html_url": "https://github.com/fastapi/fastapi",
    "stars": 104676,
    "owner": "fastapi",
    "language": "Python",
    "description": "FastAPI framework, high performance, easy to learn, fast to code, ready for production"
  },
  {
    "name": "headroom",
    "full_name": "headroomlabs-ai/headroom",
    "clone_url": "https://github.com/headroomlabs-ai/headroom.git",
    "html_url": "https://github.com/headroomlabs-ai/headroom",
    "stars": 79511,
    "owner": "headroomlabs-ai",
    "language": "Python",
    "description": "Compress tool outputs, logs, files, and RAG chunks before they reach the LLM. 20% fewer tokens for coding agents, 60-95% fewer tokens for JSON, same answers. Library, proxy, MCP server."
  },
  {
    "name": "full-stack-fastapi-template",
    "full_name": "fastapi/full-stack-fastapi-template",
    "clone_url": "https://github.com/fastapi/full-stack-fastapi-template.git",
    "html_url": "https://github.com/fastapi/full-stack-fastapi-template",
    "stars": 46239,
    "owner": "fastapi",
    "language": "TypeScript",
    "description": "Full-stack web application template with FastAPI, React, SQLModel, PostgreSQL, Vite, Tailwind CSS, shadcn/ui, FastAPI Cloud, and Docker Compose."
  }
]
```

### Bootstrap scan, verify, report, export, and doctor on Windows

`python scripts/bootstrap.py scan`, `verify`, `report`, and `python scripts/export_cloned_paths.py` exited `0`:
- Verified 4 of 44 catalog entries (`gh`, `uv`, `ruff`, and `skills.sh` via `curl -IsS --max-time 10 https://skills.sh`).
- Remaining 10 CLIs were absent on the Windows host; all 30 reference repositories were uncloned (`exported=0`).

`python scripts/bootstrap.py doctor` exited `1` (expected on Windows where `task`, `mise`, `lefthook`, and the `python3` alias are not installed; `npm.cmd` now resolves cleanly via `shutil.which`):

```text
FAIL python3 --version :: Python was not found; run without arguments to install from the Microsoft Store, or disable this shortcut from Settings > Apps > Advanced app settings > App execution aliases.
OK   git --version :: git version 2.55.0.windows.3
FAIL task --help :: missing binary: [WinError 2] The system cannot find the file specified
FAIL mise --version :: missing binary: [WinError 2] The system cannot find the file specified
OK   uv --version :: uv 0.12.3 (507230998 2026-08-07 x86_64-pc-windows-msvc)
OK   ruff --version :: ruff 0.16.8
FAIL lefthook version :: missing binary: [WinError 2] The system cannot find the file specified
OK   node --version :: v24.19.0
OK   npm --version :: 11.17.0
```
