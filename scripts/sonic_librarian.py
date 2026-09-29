#!/usr/bin/env python3
"""SonicLibrarian — organize audio files into Artist / Year - Album / Track hierarchy.

Reads embedded metadata (ID3, Vorbis, MP4) via tinytag and moves files into:
    <base>/<Album Artist>/<YYYY - Album>/<original filename>

Usage:
    python3 sonic_librarian.py <directory> [--dry-run]

Never deletes files and never overwrites: name collisions get " (2)", " (3)" suffixes.
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

try:
    from tinytag import TinyTag
except ImportError:
    print("ERROR: tinytag is required. Run: uv run --with tinytag python3 sonic_librarian.py ...")
    sys.exit(2)

AUDIO_EXTS = {".mp3", ".flac", ".m4a", ".aac", ".wav", ".ogg", ".opus", ".wma", ".aiff", ".aif"}

FORBIDDEN = set(r'\/:*?"<>|')


def sanitize_name(name: str) -> str:
    """Make a string safe as a directory name."""
    name = "".join(c for c in name if c not in FORBIDDEN)
    name = re.sub(r"[\x00-\x1f]", "", name)  # control chars
    name = re.sub(r"\s+", " ", name).strip().strip(".").strip()
    return name


def extract_year(raw) -> str:
    m = re.search(r"\d{4}", str(raw or ""))
    return m.group(0) if m else ""


def unique_path(path: Path) -> Path:
    """Return a non-existing target path, appending (2), (3), ... on collision."""
    if not path.exists():
        return path
    stem, suffix = path.stem, path.suffix
    for i in range(2, 1000):
        candidate = path.with_name(f"{stem} ({i}){suffix}")
        if not candidate.exists():
            return candidate
    return path.with_name(f"{path.stem} (collision){suffix}")


def collect_audio_files(base: Path):
    """Materialize the list BEFORE moving anything (safe iteration)."""
    files = []
    for p in base.rglob("*"):
        if not p.is_file():
            continue
        if p.name.startswith("."):
            continue
        if p.suffix.lower() in AUDIO_EXTS:
            files.append(p)
    return files


def organize(directory: str, dry_run: bool) -> int:
    base = Path(directory).expanduser().resolve()
    if not base.is_dir():
        print(f"ERROR: not a directory: {base}")
        return 1

    files = collect_audio_files(base)
    mode = "[DRY RUN] " if dry_run else ""
    if not files:
        print(f"{mode}No audio files found in {base}")
        return 0

    moved = renamed = skipped = errors = 0

    for f in files:
        try:
            tags = TinyTag.get(f)

            artist = sanitize_name(tags.albumartist or tags.artist or "") or "Unknown Artist"
            album = sanitize_name(tags.album or "") or "Unknown Album"
            year = extract_year(tags.year)

            album_folder = f"{year} - {album}" if year else album
            target_dir = base / artist / album_folder

            if f.parent == target_dir:
                skipped += 1
                continue

            target_dir.mkdir(parents=True, exist_ok=True)
            target = unique_path(target_dir / f.name)
            if target.name != f.name:
                renamed += 1

            print(f"{mode}{f.relative_to(base)}  ->  {target.relative_to(base)}")
            if not dry_run:
                shutil.move(str(f), str(target))
            moved += 1

        except Exception as e:  # noqa: BLE001 — keep going on bad files
            errors += 1
            print(f"{mode}ERROR {f.name}: {e}")

    print(f"\nSummary: {moved} moved, {renamed} renamed (collision), "
          f"{skipped} already in place, {errors} errors")
    if dry_run:
        print("Dry run only — nothing was modified. Re-run without --dry-run to apply.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Organize audio files by metadata tags.")
    parser.add_argument("directory", help="Path to the music folder")
    parser.add_argument("--dry-run", "-n", action="store_true",
                        help="Show planned moves without modifying anything")
    args = parser.parse_args()
    return organize(args.directory, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
