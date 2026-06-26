# qbittorrent-plugin-filelist

A FileList.io search plugin for qBittorrent.

## Features

- Searches [FileList.io](https://filelist.io) through its JSON API (`api.php`), so results are structured and fast.
- IMDb-ID search: paste an IMDb ID (e.g. `tt1234567`) as the query and the plugin searches by IMDb instead of by name.
- Result annotations: each result name is prefixed with its `[category]` and tagged with `[FreeLeech]`, `[2x]`, and `[Internal]` where applicable.
- Upload-date / age column: the torrent upload date is surfaced as `pub_date`, so qBittorrent can show and sort by age.
- Proxy-aware: network calls go through qBittorrent's `helpers.retrieve_url`, which honors any configured SOCKS proxy and sets a browser-like User-Agent.

## Requirements

- qBittorrent with the search engine (Python) feature enabled.
- A [FileList.io](https://filelist.io) account.
- Python 3.9+ (qBittorrent bundles and uses its own Python interpreter for search plugins).

## Install

1. In qBittorrent: **View → Search** and ensure the **Search** tab is enabled.
2. Open the **Search plugins** dialog → **Install a new one** → **Local file** → select `filelist.py`.
3. Copy `credentials.ini.example` to `credentials.ini` in qBittorrent's `engines/` folder — the same folder where the plugin was installed (the path is shown in the Search Plugins dialog) — and fill in your username and passkey from <https://filelist.io/my.php>.
4. Run a search with the **FileList** engine selected.

## Categories

The plugin maps qBittorrent's search categories onto FileList category IDs:

| qBittorrent category | FileList category IDs       |
| -------------------- | --------------------------- |
| `all`                | (no filter — all categories) |
| `movies`             | 1, 2, 3, 4, 6, 19, 20, 25, 26 |
| `tv`                 | 21, 23, 27                  |
| `music`              | 5, 11, 12                   |
| `games`              | 9, 10                       |
| `anime`              | 24                          |
| `software`           | 8, 17, 22                   |

`books` is intentionally unsupported: FileList's "Docs" category is documentaries, not e-books.

## Credentials & security

Your passkey is a secret tied to your account and your ratio — treat it like a password. Anyone with it can download on your behalf. `credentials.ini` is listed in `.gitignore`, so it is never committed. Never commit, paste, or share it; only the example template (`credentials.ini.example`) belongs in version control.

## Development / testing

The repository ships an offline test suite. Run it with:

```sh
uv run pytest -q
```

The tests inject fake `helpers` and `novaprinter` modules via `tests/conftest.py`, so no network access and no qBittorrent installation are required.

For a manual end-to-end run against the live tracker:

```sh
uv run python filelist.py movies "ubuntu"
```

This requires a real `credentials.ini` placed next to `filelist.py`. It prints pipe-delimited result lines to stdout and any errors to stderr.

## Logging

The plugin writes a log to `filelist.log` in the same folder as `filelist.py` (next to `credentials.ini`). It records one line per search with the query, category, and result count, plus errors (bad credentials, failed requests, skipped malformed result rows). Your passkey is always redacted (`***`) before anything is written, and the log is size-capped (rotates at ~512 KB, keeping 2 old files). The file is created lazily — nothing is written until the first log entry — and it is gitignored so it never gets committed. Check it after a search that misbehaved to see what went wrong.

## How it works

qBittorrent calls `search(what, cat)` on the `filelist` class. That method loads your credentials, optionally detects an IMDb ID in the query, and calls FileList's `api.php` with the matching category IDs. Each returned torrent is shaped into a result dict and handed to qBittorrent's `prettyPrinter`, one call per result.
