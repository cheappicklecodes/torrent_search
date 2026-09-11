# 🔎 Torrent Searcher

A fast, terminal-based torrent search and download tool written in Python.

Search multiple indexers in parallel, browse deduplicated results, and download selected torrents directly from the command line.

> **For legitimate use only.** Download and share only content you have the legal right to access.

---

## ✨ Features

* ⚡ Parallel searching across multiple indexers
* 🔎 Simple interactive search
* 📊 Rich terminal result tables
* 🧹 Automatic deduplication using torrent infohashes
* 🌱 Results ranked by seeders
* 📥 Built-in BitTorrent downloading
* 📈 Live progress, speed, ETA, peers, and seeds
* 📄 Paginated results
* 🖥️ Windows, Linux, and macOS support

---

## 📋 Requirements

* **Python 3.9–3.11**
* Windows, Linux, or macOS
* Internet connection
* ~50 MB disk space

> **Python 3.11 is recommended**, particularly on Windows, because compatible `libtorrent` wheels may not be available for newer Python versions.

Check your Python version:

```bash
python --version
```

---

# 🚀 Installation

## 1. Install Python

Download Python 3.11 from:

[python.org/downloads](https://www.python.org/downloads/?utm_source=chatgpt.com)

On Windows, make sure **Add python.exe to PATH** is enabled during installation.

---

## 2. Clone the Repository

```bash
git clone https://github.com/cheappicklecodes/torrent_search
cd torrent_search
```

Alternatively, download the repository as a ZIP from GitHub and extract it.

---

## 3. Create a Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 4. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If `libtorrent` fails to install on Windows, try:

```bash
pip install libtorrent-binary
```

Then change the import in `download.py` if required:

```python
import libtorrent as lt
```

to:

```python
import libtorrent_binary as lt
```

---

## ✅ Verify Installation

Check the search dependencies:

```bash
python -c "import requests, bs4, rich; print('search deps OK')"
```

Check `libtorrent`:

```bash
python -c "import libtorrent; print('libtorrent', libtorrent.__version__)"
```

---

# ▶️ Usage

Start the application:

```bash
python cli.py
```

You'll see:

```text
╭──────────────────────────────────────╮
│ Torrent Searcher                     │
│ commands: /s <query>  /src  /next    │
│           /prev  /d <#>  /quit       │
╰──────────────────────────────────────╯
>
```

---

## 🔎 Search

Type a query directly:

```text
> ubuntu 24.04 desktop
```

The application searches enabled indexers in parallel and displays the results.

Example:

```text
┌────┬──────────────────────────────────────────────┬──────────┬──────┬──────┬────────────────┐
│ #  │ Name                                         │ Size     │ S    │ L    │ Src            │
├────┼──────────────────────────────────────────────┼──────────┼──────┼──────┼────────────────┤
│ 1  │ ubuntu-24.04.1-desktop-amd64.iso             │ 5.7 GB   │ 2841 │ 312  │ TPB            │
│ 2  │ Ubuntu 24.04 LTS Desktop [official]          │ 5.8 GB   │ 1204 │ 156  │ BitSearch      │
│ 3  │ ubuntu-24.04-desktop-amd64.iso               │ 5.7 GB   │ 892  │ 78   │ SolidTorrents  │
└────┴──────────────────────────────────────────────┴──────────┴──────┴──────┴────────────────┘

page 1 of 3 | 43 total
```

### Result fields

| Field  | Description    |
| ------ | -------------- |
| `#`    | Result number  |
| `Name` | Torrent name   |
| `Size` | Download size  |
| `S`    | Seeders        |
| `L`    | Leechers       |
| `Src`  | Source indexer |

Results are sorted by seeders and deduplicated using the torrent infohash.

---

# ⌨️ Commands

| Command      | Description                     |
| ------------ | ------------------------------- |
| `your query` | Search directly                 |
| `/s <query>` | Search for a query              |
| `/d <#>`     | Download a result               |
| `/next`      | Next page                       |
| `/prev`      | Previous page                   |
| `/src`       | List enabled indexers           |
| `/quit`      | Exit                            |
| `/q`         | Exit                            |
| `exit`       | Exit                            |
| `Ctrl+C`     | Interrupt the current operation |

---

# 📥 Downloading

Select a result by its number:

```text
> /d 1
```

Example:

```text
downloading: ubuntu-24.04.1-desktop-amd64.iso
from TPB | 5.7 GB | 2841 seeders

downloading ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 42.3%
2.4 GB  8.7 MB/s  ETA 0:04:12
peers:184 seeds:62
```

When complete:

```text
done: ubuntu-24.04.1-desktop-amd64.iso
files in ./downloads
```

Downloads are stored in:

```text
./downloads/
```

The directory is created automatically.

---

# 🛠️ Troubleshooting

### `libtorrent not installed`

Install it manually:

```bash
pip install libtorrent
```

If you're using Python 3.12+, switch to Python 3.11.

---

### No results

Try a shorter or broader search query.

You can also check which indexers are enabled:

```text
> /src
```

---

### Download stuck at 0%

The torrent may have no active seeders or peers. Try another available result.

---

### Slow download

BitTorrent speeds depend primarily on the swarm and your network.

Check:

* Seeder availability
* Internet connection
* Firewall settings
* Router configuration
* VPN performance
* ISP traffic management

---

# 🔐 Privacy & Legal

BitTorrent is a peer-to-peer protocol. Your IP address may be visible to other peers participating in the same swarm.

This application does **not** provide anonymity or privacy protection.

Use the software responsibly and comply with the laws applicable to you. Only download or distribute content you are legally permitted to access.

---

## 📄 License

Add your project's license here.

For example:

```text
MIT License
```

---

**Built with Python 🐍**
