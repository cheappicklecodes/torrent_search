# torrent-search

A command-line tool that aggregates torrent search results from multiple
public indexers and downloads via libtorrent.

## Features

- Parallel search across five public indexer APIs
- Results deduplicated by infohash, sorted by seeder count
- libtorrent-based downloader with live progress display
- uTP + TCP, DHT, PEX, LSD enabled for wide peer discovery
- No client-side download or upload rate limits

## Supported indexers

| Source | Type | API |
|---|---|---|
| The Pirate Bay | general | apibay.org JSON |
| YTS | movies | yts.mx JSON |
| BitSearch | general | HTML scrape |
| SolidTorrents | general | JSON API |
| Nyaa | anime | HTML scrape |

Indexers are defined in `search.py`. Adding a new one means writing a
function that returns a list of normalized dicts — see existing
implementations for the shape.

## Install

```bash
pip install -r requirements.txt
