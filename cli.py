# language: Python 3.11+, file: cli.py
# *interactive CLI — search, pick, download. live progress display.*

import time
import threading
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.progress import Progress, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn

from search import search_all
from download import build_session, TorrentDownload, HAS_LT

console = Console()


def do_search(query, sources=None):
    with console.status(f"[cyan]searching '{query}' across indexers..."):
        results, errors = search_all(query, sources=sources)
    if errors:
        for e in errors:
            console.print(f"[yellow]warn:[/] {e}")
    return results


def show_results(results, page=0, per_page=15):
    if not results:
        console.print("[red]no results[/]")
        return []
    start = page * per_page
    end = start + per_page
    slice_ = results[start:end]

    table = Table(show_header=True, header_style="bold cyan", expand=True)
    table.add_column("#", width=4, justify="right")
    table.add_column("Name", overflow="fold")
    table.add_column("Size", width=10)
    table.add_column("S", width=6, justify="right")
    table.add_column("L", width=6, justify="right")
    table.add_column("Src", width=14)

    for i, r in enumerate(slice_):
        table.add_row(
            str(start + i + 1),
            r["name"][:80],
            r["size"],
            f"[green]{r['seeders']}[/]",
            f"[red]{r['leechers']}[/]",
            r["source"],
        )
    console.print(table)
    console.print(f"[dim]page {page+1} of {(len(results)-1)//per_page + 1} | {len(results)} total[/]")
    return slice_


def format_speed(bps):
    for unit in ("B/s", "KB/s", "MB/s", "GB/s"):
        if bps < 1024:
            return f"{bps:.1f} {unit}"
        bps /= 1024
    return f"{bps:.1f} TB/s"


def format_size(n):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def run_download(magnet, name, download_dir="./downloads"):
    if not HAS_LT:
        console.print("[red]libtorrent not installed. run: pip install libtorrent[/]")
        return

    session, trackers = build_session(download_dir)
    console.print(f"[cyan]adding torrent:[/] {name[:80]}")
    dl = TorrentDownload(session, magnet, download_dir, trackers)

    with Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.1f}%",
        DownloadColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
    ) as progress:
        task = progress.add_task("downloading", total=None)

        while True:
            st = dl.status()
            progress.update(
                task,
                completed=st["total_done"],
                total=st["total"] if st["total"] else None,
                description=f"[cyan]{st['name'][:40]}[/] peers:{st['num_peers']} seeds:{st['num_seeds']}",
            )
            if st["state"] == "seeding" or (st["total"] > 0 and st["total_done"] >= st["total"]):
                break
            time.sleep(0.5)

    console.print(f"[green]done:[/] {name}")
    console.print(f"[dim]files in {download_dir}[/]")


def main():
    console.print(Panel.fit(
        "[bold cyan]Torrent Searcher[/]\n"
        "[dim]commands: /s <query>  /src  /next  /prev  /d <#>  /quit[/]",
        border_style="cyan"
    ))

    download_dir = "./downloads"
    last_results = []
    last_shown = []
    page = 0

    while True:
        try:
            cmd = console.input("[bold green]> [/]").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not cmd:
            continue

        if cmd in ("/quit", "/q", "exit"):
            break

        if cmd.startswith("/s "):
            query = cmd[3:].strip()
            last_results = do_search(query)
            page = 0
            last_shown = show_results(last_results, page)
            continue

        if cmd == "/next":
            if not last_results:
                console.print("[red]do a search first[/]")
                continue
            page += 1
            last_shown = show_results(last_results, page)
            continue

        if cmd == "/prev":
            if not last_results:
                continue
            page = max(0, page - 1)
            last_shown = show_results(last_results, page)
            continue

        if cmd.startswith("/d "):
            try:
                idx = int(cmd[3:].strip())
                r = last_results[idx - 1]
            except (ValueError, IndexError):
                console.print("[red]invalid number[/]")
                continue
            console.print(f"[cyan]downloading:[/] {r['name'][:80]}")
            console.print(f"[dim]from {r['source']} | {r['size']} | {r['seeders']} seeders[/]")
            run_download(r["magnet"], r["name"], download_dir)
            continue

        if cmd == "/src":
            console.print("sources: tpb, yts, bitsearch, solid, nyaa")
            continue

        # default: treat as search
        last_results = do_search(cmd)
        page = 0
        last_shown = show_results(last_results, page)


if __name__ == "__main__":
    main()