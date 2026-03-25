# 🤖 Github Agent (Auto-Collector)

An intelligent Python agent designed to automate the search, collection, and archiving of GitHub repositories based on specific keywords and popularity. Ideal for creating code datasets, researching specific implementations, or mass-downloading resources for offline analysis.

## 🚀 Features
- **Smart Search**: Uses the GitHub API to find the highest-starred repositories for any query.
- **High-Speed Parallel Cloning**: Utilizes multi-threading for blazing-fast downloads.
- **Auto-Cleaning**: Drops `.git` history folders automatically to drastically reduce zip sizes.
- **Automatic Archiving**: Bundles everything into a single `.zip` file with a detailed research report.

## 🛠 Tech Stack & Agentic Tooling
This project is bootstrapped and governed by a comprehensive agentic execution stack, enforcing standardized patterns and maximum operational leverage.

### Core Agent Workflow & Intelligence
- **[Skills & Skills-CLI](https://skills.sh)**: Reusable domain workflows, progressive disclosure of capabilities, and modular logic injection.
- **[Subagents](https://github.com/VoltAgent/awesome-claude-code-subagents)**: Isolated execution contexts for high-compute, parallelized, and feature-specific workflows.
- **[Claude-Mem](https://github.com/thedotmack/claude-mem)**: Persistent memory context extending across independent debugging and development sessions.
- **[CCPM (Claude Code Project Management)](https://github.com/automazeio/ccpm)**: Structured execution tracking, issue lifecycle management, and transparent task ownership.
- **[MCP (Model Context Protocol)](https://github.com/modelcontextprotocol/servers)**: Native connections mapping database schemas and external APIs into the agent's context.
- **[Spec-Kit](https://github.com/github/spec-kit)**: Translates ambiguous product requirements into strict, actionable development specs.

### Repo, Build & Environment Operations
- **[mise](https://github.com/jdx/mise)**: Polyglot version manager ensuring exact runtime versions.
- **[Task](https://taskfile.dev/)**: YAML-based native task runner to standardize workspace routines and builds.
- **[Lefthook](https://github.com/evilmartians/lefthook)**: High-speed git hook manager enforcing validation at the pre-commit boundary.
- **[gh (GitHub CLI)](https://cli.github.com/)**: Native PR, issue, and automated repo operations.

### Python Foundation
- **[uv](https://github.com/astral-sh/uv)**: Blazing-fast Python package installer and virtual environment manager.
- **[Ruff](https://github.com/astral-sh/ruff)**: Ultra-fast Rust-based static analysis, linting, and formatting.

## 📦 Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Anwarito-lbd/Github-agent.git
   cd Github-agent
   ```

2. Bootstrap the environment:
   ```bash
   task setup
   ```
   *(This uses `uv` to create a virtual environment, syncs `requirements.txt`, and active the `lefthook` Git hooks).*

## 💻 Usage
Run the script to start the interactive CLI:
```bash
# Assuming you actived your venv: `source .venv/bin/activate`
python github.agent.py
```

1. **GitHub Token** *(Optional)*: Enter a Personal Access Token to avoid hitting API rate limits.
2. **Search Query**: e.g., `trading bot python`, `machine learning`.
3. **Quantity**: How many repositories to download (e.g., 10, 50).

**Output**: A clean, history-free `GITHUB_<query>_<time>.zip` archive generated right in the `github_agent_downloads/` directory.

## 🧹 Development Commands
- `task setup`: Initializes the workspace (`uv venv`, dependencies, `lefthook`).
- `task lint`: Run `ruff check` on the codebase.
- `task format`: Apply automated formatting with `ruff format`.

## ⚠️ Disclaimer
Intended for educational and research purposes. Ensure you comply with the open-source licenses of downloaded repositories and respect GitHub's API rate limits.
