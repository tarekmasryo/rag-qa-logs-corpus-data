"""Generate (or verify) SHA-256 checksums for repo data assets.

Usage:
  python scripts/make_checksums.py           # write checksums.sha256
  python scripts/make_checksums.py --check   # verify checksums.sha256 matches current files
"""

import argparse
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "checksums.sha256"


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def iter_target_files() -> list[Path]:
    patterns = [
        "data/*.csv",
        "docs/*.csv",
        "data_dictionary.csv",
        "README.md",
        "LICENSE",
        "CITATION.cff",
        "CHANGELOG.md",
    ]
    files: list[Path] = []
    for pat in patterns:
        files.extend(ROOT.glob(pat))

    # Keep only files that exist, deterministic order, and store as relative paths.
    files = [p for p in files if p.is_file()]
    files.sort(key=lambda p: str(p.relative_to(ROOT)).lower())
    return files


def build_lines() -> list[str]:
    lines: list[str] = []
    for path in iter_target_files():
        rel = path.relative_to(ROOT).as_posix()
        digest = sha256_file(path)
        lines.append(f"{digest}  {rel}")
    return lines


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--check",
        action="store_true",
        help="Verify checksums.sha256 instead of writing it",
    )
    args = ap.parse_args()

    lines = build_lines()
    content = "\n".join(lines) + "\n"

    if args.check:
        if not OUT_FILE.exists():
            print("checksums.sha256 is missing. Generate it with: python scripts/make_checksums.py")
            return 2
        existing = OUT_FILE.read_text(encoding="utf-8")
        if existing != content:
            print("checksums.sha256 does not match current files.")
            print("Re-generate with: python scripts/make_checksums.py")
            return 1
        print("checksums.sha256 OK")
        return 0

    OUT_FILE.write_text(content, encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(ROOT)} ({len(lines)} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
