#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    cache_dir = root / ".tools-cache"
    out_dir = root / ".bootstrap"
    out_dir.mkdir(parents=True, exist_ok=True)

    dirs = (
        sorted([p for p in cache_dir.iterdir() if p.is_dir()])
        if cache_dir.exists()
        else []
    )

    txt_path = out_dir / "cloned_repo_paths.txt"
    md_path = out_dir / "cloned_repo_paths.md"

    txt_lines = [str(p.resolve()) for p in dirs]
    txt_path.write_text(
        "\n".join(txt_lines) + ("\n" if txt_lines else ""), encoding="utf-8"
    )

    md_lines = ["# Cloned Repo Paths", ""]
    if dirs:
        for p in dirs:
            md_lines.append(f"- `{p.resolve()}`")
    else:
        md_lines.append("- No cloned repos found in `.tools-cache/`.")
    md_lines.append("")
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    print(f"exported={len(dirs)}")
    print(f"txt={txt_path}")
    print(f"md={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
