#!/usr/bin/env python3

"""
GITHUB AGENT - COLLECTOR
------------------------
Autonomous repository collector that:
1. Resolves GitHub API credentials (CLI flag, env var, or interactive prompt).
2. Queries the GitHub REST Search API with pagination and rate-limit handling.
3. Shallow-clones matched repositories in parallel without leaking tokens in URLs.
4. Strips `.git` metadata and packages a ZIP archive with a search report.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    import requests
    from tqdm import tqdm
except ImportError:
    print("❌ Erreur : Il manque des librairies.")
    print("Veuillez lancer : pip install -r requirements.txt")
    sys.exit(1)

# =====================================================
# Configuration
# =====================================================

BASE_DIR = Path.cwd() / "github_agent_downloads"
WORK_DIR = BASE_DIR / "temp_repos"
GITHUB_SEARCH_API_URL = "https://api.github.com/search/repositories"
GITHUB_API_VERSION = "2022-11-28"
MAX_SEARCH_PAGES = 10
MAX_PER_PAGE = 100
DEFAULT_WORKERS = 8
MAX_WORKERS = 16

# =====================================================
# Utility Helpers
# =====================================================


def clean_filename(text: str) -> str:
    """Sanitize directory and archive names for Windows/Linux filesystems."""
    return re.sub(r"[^\w\-_]", "_", text)


def print_banner() -> None:
    print("\n" + "=" * 60)
    print("      🤖 GITHUB AUTO-COLLECTOR AGENT")
    print("      Recherche -> Clone -> Zip")
    print("=" * 60 + "\n")


def check_git_installed() -> bool:
    """Return True when the `git` CLI is callable on PATH."""
    try:
        result = subprocess.run(
            ["git", "--version"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        return False
    return result.returncode == 0


def resolve_token(cli_token: str | None = None) -> str:
    """Resolve a GitHub token from explicit flag, GITHUB_TOKEN, or GH_TOKEN."""
    if cli_token and cli_token.strip():
        return cli_token.strip()
    for env_var in ("GITHUB_TOKEN", "GH_TOKEN"):
        val = os.environ.get(env_var, "").strip()
        if val:
            return val
    return ""


def build_search_query(
    query: str,
    language: str | None = None,
    min_stars: int | None = None,
) -> str:
    """Append optional GitHub search qualifiers without duplicating existing ones."""
    parts = [query.strip()]
    lowered = query.lower()
    if language and "language:" not in lowered:
        parts.append(f"language:{language.strip()}")
    if min_stars is not None and min_stars > 0 and "stars:" not in lowered:
        parts.append(f"stars:>={min_stars}")
    return " ".join(part for part in parts if part)


def build_git_headers(token: str) -> dict[str, str]:
    """Build GitHub REST API v3 request headers."""
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "Github-Agent-v2",
        "X-GitHub-Api-Version": GITHUB_API_VERSION,
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def build_git_auth_env(token: str) -> dict[str, str]:
    """Build subprocess env passing GitHub auth via GIT_CONFIG_* instead of URLs."""
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    if token:
        basic_bytes = f"x-access-token:{token}".encode()
        encoded = base64.b64encode(basic_bytes).decode("ascii")
        env["GIT_CONFIG_COUNT"] = "1"
        env["GIT_CONFIG_KEY_0"] = "http.https://github.com/.extraheader"
        env["GIT_CONFIG_VALUE_0"] = f"AUTHORIZATION: basic {encoded}"
    return env


def _handle_remove_readonly(func: Any, path: str, _exc: Any) -> None:
    """Clear read-only bits (e.g. git packfiles on Windows) before retrying unlink."""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def remove_tree(path: Path) -> None:
    """Remove a directory tree cleanly across Windows and POSIX."""
    if not path.exists():
        return
    shutil.rmtree(path, onexc=_handle_remove_readonly)


def _format_rate_limit_message(response: requests.Response) -> str:
    """Format a diagnostic message from GitHub rate-limit response headers."""
    remaining = response.headers.get("X-RateLimit-Remaining")
    reset_raw = response.headers.get("X-RateLimit-Reset")
    retry_after = response.headers.get("Retry-After")

    details: list[str] = [f"HTTP {response.status_code}"]
    if remaining is not None:
        details.append(f"remaining={remaining}")
    if retry_after:
        details.append(f"retry_after={retry_after}s")
    if reset_raw and reset_raw.isdigit():
        reset_dt = datetime.fromtimestamp(int(reset_raw), tz=UTC)
        details.append(f"resets_at={reset_dt.strftime('%Y-%m-%dT%H:%M:%SZ')}")
    return ", ".join(details)


# =====================================================
# 1. Search Module (GitHub REST Search API)
# =====================================================


def search_github(
    query: str,
    limit: int,
    token: str,
    *,
    session: requests.Session | None = None,
    timeout: int = 10,
    max_retries: int = 1,
    retry_backoff: float = 1.0,
) -> list[dict[str, Any]]:
    """Query GitHub Search API for top starred repositories matching `query`."""
    if limit <= 0 or not query.strip():
        return []

    print(f"\n🔎 Recherche des {limit} meilleurs dépôts pour : '{query}'...")

    headers = build_git_headers(token)
    owns_session = session is None
    http = session or requests.Session()

    repos_found: list[dict[str, Any]] = []
    seen_full_names: set[str] = set()
    page = 1

    try:
        while len(repos_found) < limit and page <= MAX_SEARCH_PAGES:
            per_page = min(MAX_PER_PAGE, max(1, limit - len(repos_found)))
            params = {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": per_page,
                "page": page,
            }

            response: requests.Response | None = None
            for attempt in range(max_retries + 1):
                try:
                    response = http.get(
                        GITHUB_SEARCH_API_URL,
                        headers=headers,
                        params=params,
                        timeout=timeout,
                    )
                except requests.RequestException as exc:
                    print(f"❌ Erreur de connexion : {exc}")
                    response = None
                    break

                if response.status_code >= 500 and attempt < max_retries:
                    if retry_backoff > 0:
                        time.sleep(retry_backoff * (attempt + 1))
                    continue
                break

            if response is None:
                break

            if response.status_code == 401:
                print("❌ Erreur : Votre Token est invalide ou expiré (HTTP 401).")
                return []
            if response.status_code in {403, 429}:
                diag = _format_rate_limit_message(response)
                print(f"⚠️ Limite d'API GitHub atteinte ({diag}).")
                break
            if response.status_code == 422:
                print("❌ Erreur : Requête de recherche GitHub invalide (HTTP 422).")
                return []
            if response.status_code != 200:
                print(f"⚠️ Erreur API ({response.status_code})")
                break

            data = response.json()
            items = data.get("items", [])
            if not items:
                break

            for item in items:
                full_name = item["full_name"]
                if full_name in seen_full_names:
                    continue
                seen_full_names.add(full_name)
                repos_found.append(
                    {
                        "name": item["name"],
                        "full_name": full_name,
                        "clone_url": item["clone_url"],
                        "html_url": item.get("html_url", ""),
                        "stars": item["stargazers_count"],
                        "owner": item["owner"]["login"],
                        "language": item.get("language") or "",
                        "description": item.get("description") or "",
                    }
                )
                if len(repos_found) >= limit:
                    break

            total_count = data.get("total_count")
            if isinstance(total_count, int) and len(repos_found) >= total_count:
                break
            if len(items) < per_page:
                break

            page += 1
    finally:
        if owns_session:
            http.close()

    repos_found.sort(key=lambda x: x["stars"], reverse=True)
    return repos_found[:limit]


# =====================================================
# 2. Clone & Package Module
# =====================================================


def clone_single_repo(
    repo_info: dict[str, Any],
    token: str,
    *,
    work_dir: Path | None = None,
    timeout: int = 180,
) -> dict[str, Any] | None:
    """Shallow-clone a single repository into `work_dir` and strip its `.git` folder."""
    target_root = work_dir or WORK_DIR
    folder_name = clean_filename(f"{repo_info['name']}_{repo_info['owner']}")
    target_path = target_root / folder_name

    if target_path.exists():
        return None

    clone_url = repo_info["clone_url"]
    env = build_git_auth_env(
        token if clone_url.startswith("https://github.com/") else ""
    )

    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", clone_url, str(target_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout,
            check=True,
            env=env,
        )

        git_hidden = target_path / ".git"
        if git_hidden.exists():
            remove_tree(git_hidden)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        remove_tree(target_path)
        return None
    else:
        return repo_info


def write_report(
    report_file: Path,
    query: str,
    limit: int,
    success_count: int,
    repos: list[dict[str, Any]],
    timestamp: str,
) -> None:
    """Write a plain-text search and download summary report."""
    with open(report_file, "w", encoding="utf-8") as handle:
        handle.write(f"Rapport généré le {timestamp} UTC\n")
        handle.write(f"Recherche : {query}\n")
        handle.write(f"Projets demandés : {limit}\n")
        handle.write(f"Projets téléchargés : {success_count}\n")
        handle.write("-" * 30 + "\n")
        handle.writelines(
            f"[{r['stars']}★] {r['full_name']} -> {r['clone_url']}\n" for r in repos
        )


def package_repos(
    repos: list[dict[str, Any]],
    *,
    query: str,
    limit: int,
    token: str,
    base_dir: Path | None = None,
    work_dir: Path | None = None,
    workers: int = DEFAULT_WORKERS,
) -> tuple[int, Path]:
    """Clone `repos` concurrently, write the report, and archive them to a ZIP file."""
    out_base = base_dir or BASE_DIR
    staging_dir = work_dir or (out_base / "temp_repos")

    remove_tree(staging_dir)
    staging_dir.mkdir(parents=True, exist_ok=True)

    worker_count = max(1, min(MAX_WORKERS, workers))
    success_count = 0

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = [
            executor.submit(clone_single_repo, repo, token, work_dir=staging_dir)
            for repo in repos
        ]
        for future in tqdm(
            futures, total=len(repos), desc="⬇️  Téléchargement", unit="repo"
        ):
            if future.result():
                success_count += 1

    timestamp = datetime.now(tz=UTC).strftime("%Y-%m-%d_%Hh%Mm")
    report_file = staging_dir / "_RAPPORT_DE_RECHERCHE.txt"
    write_report(report_file, query, limit, success_count, repos, timestamp)

    print("\n📦 Création de l'archive ZIP...")
    safe_query_name = clean_filename(query)
    zip_stem = out_base / f"GITHUB_{safe_query_name}_{timestamp}"
    archive_path = Path(shutil.make_archive(str(zip_stem), "zip", staging_dir))

    remove_tree(staging_dir)
    return success_count, archive_path


# =====================================================
# CLI Entrypoint
# =====================================================


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments while preserving interactive mode when `--query` is omitted."""
    parser = argparse.ArgumentParser(
        description="Search GitHub repositories, shallow-clone them concurrently, and package a ZIP."
    )
    parser.add_argument(
        "-q",
        "--query",
        help="GitHub repository search query. Omit to launch interactive prompts.",
    )
    parser.add_argument(
        "-n",
        "--limit",
        type=int,
        default=10,
        help="Maximum number of repositories to collect (default: 10).",
    )
    parser.add_argument(
        "-l",
        "--language",
        help="Optional language qualifier appended to the search query.",
    )
    parser.add_argument(
        "--min-stars",
        type=int,
        default=None,
        help="Optional minimum stars qualifier (stars:>=N).",
    )
    parser.add_argument(
        "-t",
        "--token",
        default=None,
        help="GitHub token. Falls back to GITHUB_TOKEN or GH_TOKEN if set.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
        help=f"Concurrent git clone workers (1-{MAX_WORKERS}, default: {DEFAULT_WORKERS}).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory for generated ZIP archives.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Query the GitHub Search API and display results without cloning or zipping.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Emit search results as JSON (for automation or dry-run pipelines).",
    )
    return parser.parse_args(argv)


def _prompt_interactive_inputs(cli_token: str | None) -> tuple[str, str, int]:
    """Collect token, query, and limit interactively when `--query` is omitted."""
    print("📝 VEUILLEZ RÉPONDRE AUX QUESTIONS :\n")

    env_token = resolve_token(cli_token)
    if env_token:
        print("1. Token GitHub détecté via l'environnement (GITHUB_TOKEN/GH_TOKEN).")
        user_token = env_token
    else:
        print("1. Collez votre Token GitHub (Classic) pour l'accès API.")
        print(
            "   (Si vous n'en avez pas, appuyez juste sur Entrée, mais la recherche sera limitée)"
        )
        user_token = input("   👉 Token : ").strip()

    print(
        "\n2. Que cherchez-vous ? (ex: 'trading bot python', 'portfolio react', 'django ecommerce')"
    )
    user_query = input("   👉 Recherche : ").strip()
    if not user_query:
        print("❌ Vous devez écrire quelque chose !")
        sys.exit(1)

    print("\n3. Combien de projets voulez-vous télécharger ? (ex: 10, 50, 100)")
    try:
        count_str = input("   👉 Nombre : ").strip()
        user_limit = int(count_str)
    except ValueError:
        user_limit = 10
        print("⚠️ Nombre invalide, on part sur 10 par défaut.")

    return user_token, user_query, user_limit


def _print_dry_run_results(repos: list[dict[str, Any]], *, json_output: bool) -> None:
    if json_output:
        print(json.dumps(repos, indent=2, ensure_ascii=False))
        return
    print("\n🧪 Mode dry-run (aucun clonage ni archive ZIP) :")
    for repo in repos:
        lang = f" [{repo['language']}]" if repo.get("language") else ""
        print(
            f"  - [{repo['stars']}★] {repo['full_name']}{lang} -> {repo['clone_url']}"
        )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if not args.json_output:
        print_banner()

    if not args.dry_run and not check_git_installed():
        print("❌ Erreur : GIT n'est pas installé sur cet ordinateur.")
        print("Installez Git ici : https://git-scm.com/downloads")
        sys.exit(1)

    if args.query is not None:
        user_token = resolve_token(args.token)
        raw_query = args.query.strip()
        if not raw_query:
            print("❌ Vous devez écrire quelque chose !")
            sys.exit(1)
        user_query = build_search_query(
            raw_query,
            language=args.language,
            min_stars=args.min_stars,
        )
        user_limit = max(1, args.limit)
    else:
        user_token, raw_query, user_limit = _prompt_interactive_inputs(args.token)
        user_query = build_search_query(
            raw_query,
            language=args.language,
            min_stars=args.min_stars,
        )

    repos = search_github(user_query, user_limit, user_token)
    if not repos:
        if args.json_output:
            print("[]")
        else:
            print("\n❌ Aucun dépôt trouvé. Fin du programme.")
        return 0

    if args.dry_run:
        _print_dry_run_results(repos, json_output=args.json_output)
        return 0

    print(f"\n✅ {len(repos)} projets identifiés. Démarrage du téléchargement...")
    out_base = args.output_dir or BASE_DIR
    success_count, archive_path = package_repos(
        repos,
        query=user_query,
        limit=user_limit,
        token=user_token,
        base_dir=out_base,
        work_dir=out_base / "temp_repos",
        workers=args.workers,
    )

    if args.json_output:
        print(
            json.dumps(
                {
                    "query": user_query,
                    "requested": user_limit,
                    "cloned": success_count,
                    "archive": str(archive_path),
                    "repositories": repos,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0

    print("\n" + "=" * 60)
    print("✅ MISSION ACCOMPLIE !")
    print(f"📊 Dépôts clonés : {success_count}/{len(repos)}")
    print("📂 Votre fichier est prêt ici :")
    print(f"   👉 {archive_path}")
    print("=" * 60 + "\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\n🛑 Arrêt forcé par l'utilisateur.")
        raise SystemExit(130) from None
    except (
        requests.RequestException,
        subprocess.SubprocessError,
        OSError,
        ValueError,
    ) as e:
        print(f"\n❌ Erreur inattendue : {e}")
        raise SystemExit(1) from e
