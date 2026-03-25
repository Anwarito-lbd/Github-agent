# New Machine Bring-Up

## 1) Clone + enter
```bash
git clone https://github.com/Anwarito-lbd/Github-agent.git
cd Github-agent
```

## 2) Core setup
```bash
task setup
```

## 3) One-command full onboarding
```bash
bash scripts/onboard.sh
```

## 4) Inspect matrix
```bash
task bootstrap:report
```

## 5) If blocked by permissions/network
- Read `.bootstrap/latest_report.md`.
- Run the exact `manual install:` or `manual clone:` command shown in the row notes.
- Re-run:
```bash
task bootstrap:retry
```
