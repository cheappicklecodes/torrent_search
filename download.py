# language: Python 3.11+, file: download.py
# *libtorrent wrapper. no client-side rate caps, DHT/PEX/LSD on, uTP + TCP,*
# *high connection limits. this is the "no speed limit" part — everything*
# *torrent-side is unlocked, speed is whatever the swarm delivers.*

import os
import time
import threading
from pathlib import Path

try:
    import libtorrent as lt
    HAS_LT = True
except ImportError:
    HAS_LT = False


def build_session(download_dir="downloads", port=6881):
    """configure a libtorrent session tuned for max throughput."""
    if not HAS_LT:
        raise RuntimeError(
            "libtorrent not installed. install via: pip install libtorrent\n"
            "if that fails on windows, try: python -m pip install libtorrent-binary"
        )

    Path(download_dir).mkdir(parents=True, exist_ok=True)

    settings = {
        "listen_interfaces": f"0.0.0.0:{port},[::]:{port}",
        "enable_dht": True,
        "enable_lsd": True,
        "enable_upnp": True,
        "enable_natpmp": True,

        # no throttling
        "download_rate_limit": 0,
        "upload_rate_limit": 0,

        # connection tuning — high but not insane
        "connections_limit": 800,
        "active_downloads": 8,
        "active_seeds": 12,
        "active_limit": 20,

        # protocol — uTP + TCP both on for widest peer reach
        "enable_incoming_utp": True,
        "enable_outgoing_utp": True,
        "enable_incoming_tcp": True,
        "enable_outgoing_tcp": True,

        # peer discovery
        "dht_bootstrap_nodes": "dht.libtorrent.org:25401,dht.transmissionbt.com:6881,router.bittorrent.com:6881",
        "announce_to_all_trackers": True,
        "announce_to_all_tiers": True,

        # disk + memory
        "aio_threads": 4,
        "checking_mem_usage": 2048,
        "cache_size": 1024,
        "disk_write_mode": 0,  # auto

        # useful defaults
        "user_agent": "qBittorrent/4.6.0",
        "alert_queue_size": 10000,
    }

    session = lt.session(settings)

    # add public trackers to the session
    trackers_file = Path(__file__).parent / "trackers.txt"
    tracker_list = []
    if trackers_file.exists():
        for line in trackers_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                tracker_list.append(line)

    for tr in tracker_list:
        try:
            session.add_dht_node((tr.split("://")[1].split(":")[0],
                                   int(tr.split(":")[-1].split("/")[0])))
        except Exception:
            pass  # only dht nodes can be added this way

    return session, tracker_list


class TorrentDownload:
    """wraps a single torrent handle with progress tracking."""
    def __init__(self, session, magnet_or_path, download_dir, tracker_list):
        self.session = session
        self.dir = os.path.abspath(download_dir)

        if magnet_or_path.startswith("magnet:"):
            params = lt.parse_magnet_uri(magnet_or_path)
            params.save_path = self.dir
            self.handle = session.add_torrent(params)
        elif os.path.isfile(magnet_or_path) and magnet_or_path.endswith(".torrent"):
            info = lt.torrent_info(magnet_or_path)
            params = {"ti": info, "save_path": self.dir}
            self.handle = session.add_torrent(params)
        else:
            raise ValueError("must be magnet link or .torrent file")

        # add extra trackers
        try:
            existing = self.handle.trackers()
            existing_urls = {t["url"] for t in existing}
            for tr in tracker_list:
                if tr not in existing_urls:
                    self.handle.add_tracker({"url": tr})
        except Exception:
            pass

        # sequential download off by default — parallel is faster
        self.handle.set_sequential_download(False)
        # no per-torrent caps
        self.handle.set_download_limit(0)
        self.handle.set_upload_limit(0)

    @property
    def name(self):
        try:
            return self.handle.status().name or "unknown"
        except Exception:
            return "unknown"

    def status(self):
        s = self.handle.status()
        return {
            "name": s.name,
            "progress": s.progress * 100,
            "state": str(s.state),
            "download_rate": s.download_rate,
            "upload_rate": s.upload_rate,
            "num_peers": s.num_peers,
            "num_seeds": s.num_seeds,
            "total_done": s.total_done,
            "total": s.total_wanted,
            "eta": self._eta(s),
        }

    def _eta(self, s):
        if s.download_rate <= 0 or s.total_wanted == 0:
            return -1
        remain = s.total_wanted - s.total_done
        return remain / s.download_rate

    def pause(self):
        self.handle.pause()

    def resume(self):
        self.handle.resume()

    def remove(self, delete_files=False):
        flags = lt.session.delete_files if delete_files else 0
        self.session.remove_torrent(self.handle, flags)

    def is_done(self):
        return self.handle.status().is_seeding