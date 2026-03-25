# 🤖 Github Agent (Auto-Collector)

An intelligent Python agent designed to automate the search, collection, and archiving of GitHub repositories based on specific keywords and popularity. Ideal for creating code datasets, researching specific implementations, or mass-downloading resources for offline analysis.

## 🚀 Features
- **Smart Search**: Uses the GitHub API to find the highest-starred repositories for any query.
- **High-Speed Parallel Cloning**: Utilizes multi-threading for blazing-fast downloads.
- **Auto-Cleaning**: Drops `.git` history folders automatically to drastically reduce zip sizes.
- **Automatic Archiving**: Bundles everything into a single `.zip` file with a detailed research report.

## 🛠 Tech Stack & Tooling (Modern Default)
This project is optimally configured with a modern, high-performance execution stack:
- **[uv](https://github.com/astral-sh/uv)**: Extremely fast Python package installer and resolver.
- **[ruff](https://github.com/astral-sh/ruff)**: Lightning-fast Python linter and code formatter.
- **[lefthook](https://github.com/evilmartians/lefthook)**: Fast and powerful Git hooks manager enforcing quality at the commit stage.
- **[task](https://taskfile.dev/)**: A task runner to automate standard commands (`Taskfile.yml`).

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
