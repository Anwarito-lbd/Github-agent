# Github Agent + Full Toolchain Bootstrap

Python GitHub collector plus a reproducible bootstrap control plane for your preferred engineering/product/automation stack.

## What This Repo Does
- Runs your original GitHub collector app (`github.agent.py`).
- Installs and verifies your preferred CLI stack.
- Clones and verifies all reference repos into `.tools-cache/`.
- Produces a strict bootstrap matrix report at `.bootstrap/latest_report.md`.

## Clone And Access Everything
After cloning this repo, run one command:
```bash
bash scripts/onboard.sh
```
This performs setup + install + clone + verify + report.

Alternative:
```bash
task onboard
```

## What `task bootstrap` does
Runs:
1. `scan` (detect installed/cloned/available)
2. `install` (attempt CLI installs)
3. `clone` (clone reference repos to `.tools-cache/`)
4. `verify` (version/help/README/URL checks)
5. `report` (matrix output + `.bootstrap/latest_report.md`)

Core engine:
- `scripts/bootstrap.py`
- `config/tool_catalog.json`

## Where The Other Repos Are
- All external repos are cloned to `.tools-cache/`.
- They are intentionally not committed to git history to keep this repo lightweight.
- You still get full local access after onboarding, with exact clone paths shown in the report.

## Bootstrap Matrix Format
The report prints exact columns:
- `Tool/Repo`
- `Relevant?`
- `Installed? (yes/no/already)`
- `Cloned? (yes/no/already)`
- `Verified? (yes/no)`
- `Used in plan? (yes/no)`
- `Notes`

## Blocker Behavior
If install/clone is blocked by network, sandbox, credentials, package manager, or OS mismatch:
- The row is kept unverified.
- `Notes` records the blocker details.
- `Notes` includes an exact `manual install:` or `manual clone:` command.

## Profiles and Usage
- Python/trading/data workflows: `uv`, `ruff`, `task`, `mise`, `lefthook`.
- JS/web/full-stack workflows: `biome`, `nx`, `vercel`, `supabase`.
- Automation/research/agent workflows: `playwright-cli`, `notebooklm-py`, MCP and skills repos in `.tools-cache/`.
- Startup execution workflows: `gh`, `spec-kit`, `ccpm`, task/runbook pattern.

## Commands
```bash
task doctor
task onboard
task bootstrap
task bootstrap:scan
task bootstrap:install
task bootstrap:clone
task bootstrap:verify
task bootstrap:report
task bootstrap:retry
task lint
task format
```

## Existing App Usage
Run the collector CLI:
```bash
python github.agent.py
```
Output zips are written to `github_agent_downloads/`.

## New Machine Runbook
See:
- [docs/new-machine-runbook.md](docs/new-machine-runbook.md)

## CI
GitHub Actions workflow added:
- `.github/workflows/bootstrap-check.yml`
- Runs `task bootstrap:scan` and `task doctor` on PRs/pushes.
