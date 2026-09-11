Installation
Prerequisites
Python 3.9–3.11 (libtorrent wheels don't exist for 3.12+ on Windows yet — check with python --version)

Windows / Linux / macOS

~50 MB disk for the tool itself

Step 1 — install Python (if you don't have it)
Windows: download from python.org/downloads → get 3.11.x → run installer → check "Add python.exe to PATH" → Install Now.

Verify:

text
python --version
Should print Python 3.11.x.

Linux (Debian/Ubuntu):

bash
sudo apt update && sudo apt install python3 python3-pip
macOS:

bash
brew install python@3.11
Step 2 — get the code
Option A — clone from GitHub:

bash
git clone https://github.com/YOUR_USERNAME/torrent-search.git
cd torrent-search
Option B — download ZIP:
On the GitHub repo page → green Code button → Download ZIP → extract → open terminal in that folder.

Step 3 — create a virtual environment (recommended)
Keeps the tool's dependencies separate from your system Python. If something breaks, delete the folder and start clean.

Windows:

bash
python -m venv venv
venv\Scripts\activate
Linux / macOS:

bash
python3 -m venv venv
source venv/bin/activate
You'll know it worked when your prompt shows (venv) at the start.

Step 4 — install dependencies
bash
pip install -r requirements.txt
If libtorrent fails to install (common on Python 3.12+, or older pip):

Try in order:

bash
pip install --upgrade pip
pip install libtorrent
If that still fails on Windows:

bash
pip install libtorrent-binary
Then edit download.py line ~7:

python
import libtorrent as lt
→

python
import libtorrent_binary as lt
If libtorrent won't install at all: the search half still works. Skip the download commands — you can still search indexers. Only /d needs libtorrent.

Verify install:

bash
python -c "import requests, bs4, rich; print('search deps OK')"
python -c "import libtorrent; print('libtorrent', libtorrent.__version__)"
Both should print without errors.

Usage
Start the app
bash
python cli.py
You'll see:

text
╭──────────────────────────────────────╮
│ Torrent Searcher                     │
│ commands: /s <query>  /src  /next    │
│           /prev  /d <#>  /quit       │
╰──────────────────────────────────────╯
> 
The > is a prompt. Type a search query or a slash command.

Basic search
Type a query directly at the prompt — no /s needed:

text
> ubuntu 24.04 desktop
The app fires every indexer in parallel. After 1–3 seconds:

text
┌────┬──────────────────────────────────────────────────┬────────────┬────────┬────────┬────────────────┐
│  # │ Name                                             │ Size       │      S │      L │ Src            │
├────┼──────────────────────────────────────────────────┼────────────┼────────┼────────┼────────────────┤
│  1 │ ubuntu-24.04.1-desktop-amd64.iso                 │ 5.7 GB     │   2841 │    312 │ TPB            │
│  2 │ Ubuntu 24.04 LTS Desktop [official]              │ 5.8 GB     │   1204 │    156 │ BitSearch      │
│  3 │ ubuntu-24.04-desktop-amd64.iso                   │ 5.7 GB     │    892 │     78 │ SolidTorrents  │
│  … │ …                                                │ …          │      … │      … │ …              │
└────┴──────────────────────────────────────────────────┴────────────┴────────┴────────┴────────────────┘
page 1 of 3 | 43 total
# — result number, use it with /d

Name — torrent name

Size — total download size

S — seeders (green, higher is better)

L — leechers (red)

Src — which indexer found it

Sorted by seeders, deduplicated by infohash (so the same torrent found by 3 indexers shows once).

Commands
Command	What it does
ubuntu 24.04	search (just type it)
/d 3	download result #3
/next	next 15 results
/prev	previous page
/src	list which indexers are enabled
/quit (or /q, or exit)	exit the app
Ctrl+C	force-quit if stuck
Download a result
text
> /d 1
You'll see:

text
downloading: ubuntu-24.04.1-desktop-amd64.iso
from TPB | 5.7 GB | 2841 seeders
downloading ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 42.3% 2.4 GB 8.7 MB/s 0:04:12 peers:184 seeds:62
The progress bar updates every 500ms: percentage, downloaded amount, live speed, ETA, peer count, seed count.

When it finishes:

text
done: ubuntu-24.04.1-desktop-amd64.iso
files in ./downloads
Press Ctrl+C during download to abort and return to the prompt. The partial file stays in ./downloads/.

Where files go
Everything lands in ./downloads/ relative to where you ran python cli.py. Create a downloads folder next to cli.py if it doesn't exist — the tool makes it automatically on first download.

To change the folder, edit cli.py line ~120:

python
download_dir = "./downloads"
to whatever path you want.

Example session
text
> blender 4.2
[results table, 15 rows]
> /d 2
downloading: Blender 4.2 LTS...
[progress bar, ~2 min]
done: Blender 4.2 LTS...
> /next
[results 16-30]
> /d 18
downloading: ...
[progress]
done.
> /quit
Troubleshooting
"libtorrent not installed"
You skipped step 4, or libtorrent failed to install. Run pip install libtorrent. On Python 3.12+, use 3.11 instead.

"no results"
The indexer's site might be down, or the query is too specific. Try a shorter query. Check /src to see which indexers are enabled.

"warn: TPB: HTTPSConnectionPool"
The indexer is blocked in your region or temporarily offline. The other indexers still work — the warning is per-source, doesn't break the search.

Search works, download hangs at 0%
The torrent has no active seeders. Go back to the results, pick one with more seeders. If all top results hang, the content is dead across the swarm.

Download is slow
Swarm-limited. Pick a torrent with 500+ seeders. The tool itself has no rate caps — if the swarm is fast, you'll get full speed.

Port 6881 blocked
Some ISPs or routers block the default BitTorrent port range. Edit download.py build_session() — change port=6881 to port=51413 (or any port in 49152–65535). Also enable UPnP on your router, which the tool already requests.

Firewall prompt on first run
Windows Defender Firewall will ask to allow Python to accept connections. Allow both private and public. Without this, incoming peers can't connect and you'll only get outbound connections — slower downloads.

Everything works but speeds are 100 KB/s on a popular torrent
That's not the tool. Check:

Is your VPN throttling? Some VPNs cap P2P.

Is your ISP throttling BitTorrent? Run the download without VPN for 30 seconds to compare.

Is the torrent actually popular? Check the seeder count in the results table.

Tips
Sort matters. Results are already sorted by seeders. #1 is almost always the fastest download.

Dedupe is real. The same Ubuntu ISO on TPB and BitSearch shows once, at #1 in the list, with combined seeder info.

Public trackers = visible IP. Your IP is in the swarm. If that matters where you live, use a VPN. The tool has no built-in proxy — you'd bind a VPN adapter at the OS level or set proxy in build_session() settings.

Run the search first, then download. Searching is instant and free. Downloading commits bandwidth. You can search 20 queries, pick the best, then /d.

Uninstall
bash
# deactivate the venv
deactivate

# delete the folder
rm -rf torrent-search     # linux/mac
rmdir /s torrent-search   # windows
Nothing installs system-wide except Python itself, which you probably want anyway.

Want me to add this as a docs/INSTALL.md file in the repo, or paste it directly into the README? The README version is cleaner for a small project — one file, everything visible. If the README gets long, splitting install/usage into docs/ and linking from the README is the standard move. Which do you want?


