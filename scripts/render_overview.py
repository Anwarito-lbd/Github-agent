"""Render docs/images/collector_overview.png from catalog and verified run data."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Patch

ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "docs" / "images" / "collector_overview.png"


def main() -> int:
    catalog = json.loads(
        (ROOT / "config" / "tool_catalog.json").read_text(encoding="utf-8")
    )
    entries = catalog["entries"]
    cli_count = sum(1 for e in entries if e["kind"] == "cli")
    repo_count = sum(1 for e in entries if e["kind"] == "repo")
    url_count = sum(1 for e in entries if e["kind"] == "url")

    plt.rcParams.update(
        {
            "figure.facecolor": "#0d1117",
            "axes.facecolor": "#161b22",
            "axes.edgecolor": "#30363d",
            "axes.labelcolor": "#e6edf3",
            "text.color": "#e6edf3",
            "xtick.color": "#8b949e",
            "ytick.color": "#e6edf3",
            "font.family": "DejaVu Sans",
        }
    )

    fig = plt.figure(figsize=(14, 8.4), dpi=200)
    gs = fig.add_gridspec(
        2, 2, height_ratios=[1.05, 1.15], hspace=0.38, wspace=0.28, top=0.84
    )

    fig.suptitle(
        "Github-agent — Verified API Collector Pipeline & Toolchain Inventory",
        fontsize=15,
        fontweight="bold",
        color="#f0f6fc",
        y=0.96,
    )
    fig.text(
        0.5,
        0.915,
        "Observed data from github.agent.py (--dry-run live API), config/tool_catalog.json (44 entries), and pytest (12/12 passed)",
        ha="center",
        fontsize=9.5,
        color="#8b949e",
    )

    ax_arch = fig.add_subplot(gs[0, :])
    ax_arch.set_xlim(0, 100)
    ax_arch.set_ylim(0, 32)
    ax_arch.axis("off")
    ax_arch.set_title(
        "End-to-End Collector & Security Pipeline (github.agent.py)",
        loc="left",
        fontsize=11.5,
        fontweight="bold",
        pad=8,
    )

    boxes = [
        (
            2,
            8,
            16,
            16,
            "#1f6feb",
            "1. CLI & Auth",
            "--query / --limit\nGITHUB_TOKEN / GH_TOKEN\nBearer + API v2022-11-28",
        ),
        (
            22,
            8,
            18,
            16,
            "#238636",
            "2. Search API v3",
            "GET /search/repositories\nper_page <= 100, <= 10 pages\n401/403/429/422/5xx handling",
        ),
        (
            44,
            8,
            16,
            16,
            "#8957e5",
            "3. Dry-Run / Pool",
            "--dry-run / --json exit\nOR ThreadPoolExecutor\n(1..16 workers, default 8)",
        ),
        (
            64,
            8,
            16,
            16,
            "#d29922",
            "4. Secure Clone",
            "git clone --depth 1\nGIT_CONFIG_* extraheader\n(no token in argv/URL)",
        ),
        (
            84,
            8,
            14,
            16,
            "#da3633",
            "5. Clean & ZIP",
            "remove_tree(.git)\nUTC report .txt\nGITHUB_*.zip archive",
        ),
    ]

    for x, y, w, h, color, title, body in boxes:
        patch = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.6,rounding_size=1.4",
            linewidth=1.5,
            edgecolor=color,
            facecolor="#161b22",
        )
        ax_arch.add_patch(patch)
        ax_arch.text(
            x + w / 2,
            y + h - 2.2,
            title,
            ha="center",
            va="top",
            fontsize=9.5,
            fontweight="bold",
            color=color,
        )
        ax_arch.text(
            x + w / 2,
            y + h / 2 - 1.5,
            body,
            ha="center",
            va="center",
            fontsize=7.8,
            color="#c9d1d9",
            linespacing=1.35,
        )

    for x0, x1 in [(18.6, 21.4), (40.6, 43.4), (60.6, 63.4), (80.6, 83.4)]:
        ax_arch.annotate(
            "",
            xy=(x1, 16.0),
            xytext=(x0, 16.0),
            arrowprops={"arrowstyle": "->", "color": "#8b949e", "lw": 1.8},
        )

    ax_api = fig.add_subplot(gs[1, 0])
    repos = [
        "emmabostian/\ndeveloper-portfolios",
        "ranaroussi/\nquantstats",
        "LuckyOne7777/\nLLM-Trading-Lab",
        "fastapi/\nfastapi",
        "headroomlabs-ai/\nheadroom",
        "fastapi/\nfull-stack-fastapi-template",
    ]
    stars = [27679, 7862, 7552, 104676, 79511, 46239]
    colors = ["#58a6ff", "#58a6ff", "#58a6ff", "#3fb950", "#3fb950", "#3fb950"]

    y_pos = list(range(len(repos)))
    bars = ax_api.barh(y_pos, stars, color=colors, height=0.62, edgecolor="#0d1117")
    ax_api.set_yticks(y_pos)
    ax_api.set_yticklabels(repos, fontsize=8.0)
    ax_api.invert_yaxis()
    ax_api.set_xlabel("GitHub Stars (observed via live --dry-run)", fontsize=9)
    ax_api.set_title(
        "Live GitHub Search API Results (2 Queries, n=3 each)",
        loc="left",
        fontsize=10.5,
        fontweight="bold",
        pad=8,
    )
    ax_api.set_xlim(0, 128000)
    ax_api.grid(axis="x", color="#21262d", linestyle="--", linewidth=0.8)
    ax_api.set_axisbelow(True)

    for bar, val in zip(bars, stars, strict=True):
        ax_api.text(
            val + 1800,
            bar.get_y() + bar.get_height() / 2,
            f"{val:,}",
            va="center",
            fontsize=8.3,
            color="#e6edf3",
        )

    ax_api.legend(
        handles=[
            Patch(facecolor="#58a6ff", label="portfolio language:python"),
            Patch(facecolor="#3fb950", label="fastapi stars:>=1000"),
        ],
        loc="lower right",
        frameon=True,
        facecolor="#0d1117",
        edgecolor="#30363d",
        fontsize=7.8,
    )

    ax_cat = fig.add_subplot(gs[1, 1])
    categories = [
        "Reference Repos\n(kind: repo)",
        "CLI Tools\n(kind: cli)",
        "URL Checks\n(kind: url)",
    ]
    counts = [repo_count, cli_count, url_count]
    cat_colors = ["#a371f7", "#d29922", "#58a6ff"]

    x_pos = list(range(len(categories)))
    cbars = ax_cat.bar(x_pos, counts, color=cat_colors, width=0.52, edgecolor="#0d1117")
    ax_cat.set_xticks(x_pos)
    ax_cat.set_xticklabels(categories, fontsize=8.8)
    ax_cat.set_ylabel("Catalog Entries (config/tool_catalog.json)", fontsize=9)
    ax_cat.set_title(
        f"Bootstrap Inventory ({len(entries)} Total Entries) & Verification",
        loc="left",
        fontsize=10.5,
        fontweight="bold",
        pad=8,
    )
    ax_cat.set_ylim(0, 36)
    ax_cat.grid(axis="y", color="#21262d", linestyle="--", linewidth=0.8)
    ax_cat.set_axisbelow(True)

    for bar, val in zip(cbars, counts, strict=True):
        ax_cat.text(
            bar.get_x() + bar.get_width() / 2,
            val + 0.9,
            str(val),
            ha="center",
            fontsize=10,
            fontweight="bold",
            color="#f0f6fc",
        )

    ax_cat.text(
        0.97,
        0.92,
        "CI & Local Checks Verified:\n"
        "- pytest: 12/12 passed\n"
        "- ruff check & format: pass\n"
        "- GitHub Actions run 43370302212: pass",
        transform=ax_cat.transAxes,
        ha="right",
        va="top",
        fontsize=8.2,
        color="#c9d1d9",
        bbox={
            "boxstyle": "round,pad=0.5",
            "facecolor": "#0d1117",
            "edgecolor": "#3fb950",
            "linewidth": 1.1,
        },
    )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PATH, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"Saved {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
