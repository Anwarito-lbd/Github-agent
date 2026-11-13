# Case study: a collector and a toolchain ledger

## The job

I keep two programs in this repository. `github.agent.py` collects a GitHub search into one zip. `scripts/bootstrap.py` walks a catalog of CLIs and reference repositories and writes down what is installed, cloned, and verified.

The collector is the 24 November 2025 history: the script, `requirements.txt`, and a gitignore for the zip output. On 25 March 2026 I added the catalog, the bootstrap runner, Task, mise, Lefthook, and a CI workflow that runs scan and doctor. I use the catalog as the inventory so a new machine can be compared against one list instead of a README full of install snippets.

## What the collector actually does

The loop is fixed. It stops when `git` is missing, and it stops when the query is empty. A count that is not an integer becomes 10. Search calls `https://api.github.com/search/repositories`, sorted by stars, 100 results per page, and stops at the requested count, an empty page, a non-200 response, or 10 pages. Eight workers then `git clone --depth 1`. Each success deletes `.git` so the zip is source without history. The temp directory is removed after the archive is written.

When I paste a token, the script puts it in the clone URL. That gets the clone past anonymous limits, and it also puts the token in the `git` argument list until the process exits. The next change I would make is to pass the credential through a header or an askpass helper, and to add a non-interactive mode so a search can be demonstrated without a TTY and without cloning.

## What bootstrap actually does

`config/tool_catalog.json` is the source of truth: 13 CLIs, 30 repositories, and the skills.sh URL. Nothing in that file opts an entry out, so the matrix marks all 44 rows relevant and used. Scan records detection. Install runs the catalog command. Clone is a 60 second shallow clone into `.tools-cache/`. Verify checks a CLI command, a README in a clone, or `curl` for the URL. Report prints seven columns and saves the same markdown.

`doctor` is a separate, shorter list. It checks python3, git, task, mise, uv, ruff, lefthook, node, and npm. It does not check `gh`, even though the catalog does. I kept that split visible in the README instead of pretending one command covers the whole catalog.

## What I ran on 13 November 2026

I ran this on Linux with Python 3.12.3, git 2.43.0, Node v22.23.4, and gh 2.103.0. Homebrew was absent, and so were task, mise, uv, and lefthook. `.mise.toml` asks for Python 3.13 and Node 24, so this was not the pinned toolchain.

`python3 -m py_compile` on the four Python files exited 0. `bash -n scripts/onboard.sh` exited 0. `python3 scripts/bootstrap.py doctor` exited 1: python3, git, node, and npm passed; task, mise, uv, ruff, and lefthook were missing binaries. Scan, verify, and report exited 0. Two catalog rows verified: `gh`, and skills.sh (`HTTP/2 308` to `https://www.skills.sh/`). Twelve CLIs were not installed. All 30 repositories were uncloned. The path export printed `exported=0`.

The collector has no dry-run switch. An empty query on stdin exited 1 with `Vous devez écrire quelque chose !`. I then called `search_github("portfolio language:python", 3, "")` in-process. That function only hits the API. With `requests` 2.34.2 and `tqdm` 4.70.1 installed from the unpinned requirements file, the three results were `emmabostian/developer-portfolios` (27679 stars), `ranaroussi/quantstats` (7861), and `LuckyOne7777/LLM-Trading-Lab` (7551). I did not clone them.

`Taskfile.yml` lints with ruff. Ruff was not on `PATH`, so I installed ruff 0.17.5 into a temporary prefix and ran `ruff check` and `ruff format --check` on the four Python files. Check exited 1 with 14 findings, including the unused `time` import in the collector. Format exited 1 because `github.agent.py` would be reformatted. The three scripts were already formatted. I left that code alone in the documentation commit.

The pull request's Bootstrap Checks run then failed before scan and doctor. The Setup ruff step uses `astral-sh/ruff-action@v3`, and that action's default is `ruff check`. It reported the same 14 rules. I fixed them in the next commit: removed the unused import and the encoding cookie, sorted the imports, passed `check=False` to the git version probe, narrowed the clone and search handlers, wrote the report with `writelines`, raised `TypeError` for a catalog that is not a list, kept the top-level interactive handler with an explicit `BLE001` exception, and marked the four Python entrypoints executable. `ruff format` rewrote `github.agent.py`. After that, `ruff check .` and `ruff format --check` both exited 0. The empty query still exits 1, and `search_github("portfolio language:python", 3, "")` still returns three repositories.

I did not run install, clone, `all`, or `bootstrap_retry.py`. Those mutate the machine and download 30 repositories. I did call the retry script's resolver: `github.com`, `skills.sh`, `registry.npmjs.org`, and `pypi.org` all resolved. `/opt/homebrew/Cellar` is not on this machine, which is the condition that makes the retry script print its Homebrew warning.

## What I will show, and what I will not

I will show the pipeline, the catalog, and the transcripts in `docs/PROOF_OF_WORK.md`. I will not show a green doctor run, a populated `.tools-cache/`, or a GitHub Actions result. The workflow file installs task, mise, uv, ruff, and lefthook and then runs scan and doctor. I have not watched that job run.

The gap that matters for the next pass is small and specific: a non-interactive collector path, tests around search parsing and the status matrix, pinned Python dependencies, and token handling that stays out of the clone URL.
