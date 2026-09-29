# SonicLibrarian

Turns a messy folder of music into a clean, browsable library - by
reading the tags that are already inside your files.

```
BEFORE                          AFTER
Downloads/                      Music/
├── track1.mp3                  ├── Aphex Twin
├── 02 - untitled final.mp3     │   └── 1992 - Selected Ambient Works 85-92
├── random_album ripped.flac    │       ├── 01 - Xtal.mp3
├── (5) New Song.m4a            │       └── 02 - Tha.mp3
└── ...                         ├── Unknown Artist
                                │   └── Unknown Album
                                │       └── track1.mp3
                                └── ...
```

Target hierarchy: `Artist / Year - Album / original filename`.

## What it does

- Reads embedded metadata (ID3, Vorbis comments, MP4 atoms) via
  [tinytag](https://github.com/devsnd/tinytag) - mp3, flac, m4a/aac,
  wav, ogg, opus, wma, aiff
- Prefers **album artist**, falls back to artist, then `Unknown Artist`
- Extracts the year from date tags (`2021-03-01` → `2021`)
- **Dry-run by design**: preview every move before anything is touched
- **Never deletes, never overwrites**: filename collisions get a ` (2)`
  suffix
- Leaves the rest of the folder untouched - only audio files move

## Requirements

[uv](https://docs.astral.sh/uv/) (recommended - resolves `tinytag`
automatically), or any Python 3.8+ with `pip install tinytag`.

## Usage

```bash
# preview - always run this first
uv run --with tinytag python3 scripts/sonic_librarian.py ~/music --dry-run

# apply
uv run --with tinytag python3 scripts/sonic_librarian.py ~/music
```

Example output:

```
01 - Intro.mp3            ->  Lemon Jelly/2001 - Lost Horizons/01 - Intro.mp3
inbox_b/01 - Intro.mp3    ->  Lemon Jelly/2001 - Lost Horizons/01 - Intro (2).mp3
notags.wav                ->  Unknown Artist/Unknown Album/notags.wav

Summary: 6 moved, 1 renamed (collision), 1 already in place, 0 errors
```

## Notes & limitations

- Untagged files (WAV rips are a common case) land in
  `Unknown Artist/Unknown Album`
- Filenames are preserved - the script only changes the directory
  structure
- Multi-disc sets merge into one album folder; disc-level collisions
  are resolved by renaming
- Works locally on macOS / Linux; on Windows, avoid running it on
  paths with cloud-sync placeholders (OneDrive etc.)

## Related

- [mmdc - MP3 Metadata Cleaner](https://github.com/Starmynd/mmdc) -
  clean the junk out of your tags first (feat., remix, embedded art),
  then let SonicLibrarian build the hierarchy from them.

## License

[MIT](LICENSE)
