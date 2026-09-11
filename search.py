# language: Python 3.11+, file: search.py
# *multi-indexer torrent search — TPB, YTS, BitSearch, SolidTorrents, Nyaa.
# *each indexer returns a normalized dict. errors per-source don't kill the search.*

import re
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
HEADERS = {"User-Agent": UA}
TIMEOUT = 12


def _norm(name, size, seeders, leechers, magnet, source, category=""):
    return {
        "name": name.strip(),
        "size": size,
        "seeders": int(seeders) if str(seeders).isdigit() else 0,
        "leechers": int(leechers) if str(leechers).isdigit() else 0,
        "magnet": magnet,
        "source": source,
        "category": category,
    }


# ---------- The Pirate Bay (apibay.org JSON) ----------
def search_tpb(query, category=0):
    try:
        url = f"https://apibay.org/q.php?q={requests.utils.quote(query)}&cat={category}"
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        if not isinstance(data, list):
            return []
        out = []
        for t in data:
            if t.get("id") == "0":
                continue
            name = t.get("name", "")
            infohash = t.get("info_hash", "").lower()
            if not infohash:
                continue
            magnet = (
                f"magnet:?xt=urn:btih:{infohash}"
                f"&dn={requests.utils.quote(name)}"
                f"&tr=udp://tracker.opentrackr.org:1337/announce"
                f"&tr=udp://open.tracker.cl:1337/announce"
            )
            size = _human_size(int(t.get("size", 0)))
            out.append(_norm(name, size, t.get("seeders", 0),
                             t.get("leechers", 0), magnet, "TPB",
                             _cat_name(t.get("category", "0"))))
        return out
    except Exception as e:
        return [{"error": f"TPB: {e}"}]


# ---------- YTS (movies) ----------
def search_yts(query):
    try:
        url = f"https://yts.mx/api/v2/list_movies.json?query_term={requests.utils.quote(query)}&limit=30"
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        movies = data.get("data", {}).get("movies", []) or []
        out = []
        for m in movies:
            for tor in m.get("torrents", []):
                name = f"{m.get('title')} ({m.get('year')}) [{tor.get('quality')}] [{tor.get('type')}]"
                infohash = tor.get("hash", "").lower()
                if not infohash:
                    continue
                magnet = (
                    f"magnet:?xt=urn:btih:{infohash}"
                    f"&dn={requests.utils.quote(name)}"
                    f"&tr=udp://tracker.opentrackr.org:1337/announce"
                )
                out.append(_norm(name, tor.get("size", "?"),
                                 tor.get("seeds", 0), tor.get("peers", 0),
                                 magnet, "YTS", "movies"))
        return out
    except Exception as e:
        return [{"error": f"YTS: {e}"}]


# ---------- BitSearch (JSON) ----------
def search_bitsearch(query):
    try:
        url = f"https://bitsearch.to/search?q={requests.utils.quote(query)}&sort=seeders"
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        out = []
        for card in soup.select("div.search-result, li.search-result"):
            a = card.select_one("a[href^='/torrent/']")
            if not a:
                continue
            name = a.get_text(strip=True)
            stat_divs = card.select("div.stats div, .stats span")
            seeders = leechers = 0
            size = "?"
            for d in stat_divs:
                txt = d.get_text(strip=True)
                if "Seeder" in txt:
                    m = re.search(r"(\d+)", txt)
                    seeders = int(m.group(1)) if m else 0
                elif "Leecher" in txt:
                    m = re.search(r"(\d+)", txt)
                    leechers = int(m.group(1)) if m else 0
                elif re.match(r"[\d.]+\s*(KB|MB|GB|TB)", txt):
                    size = txt
            href = a.get("href", "")
            # fetch magnet from the detail page
            if href.startswith("/"):
                detail_url = "https://bitsearch.to" + href
                try:
                    dr = requests.get(detail_url, headers=HEADERS, timeout=TIMEOUT)
                    dm = re.search(r'(magnet:\?xt=urn:btih:[a-fA-F0-9]{40}[^"\']*)', dr.text)
                    magnet = dm.group(1) if dm else ""
                except Exception:
                    magnet = ""
            else:
                magnet = ""
            if magnet:
                out.append(_norm(name, size, seeders, leechers, magnet, "BitSearch"))
        return out
    except Exception as e:
        return [{"error": f"BitSearch: {e}"}]


# ---------- SolidTorrents (JSON) ----------
def search_solid(query):
    try:
        url = f"https://solidtorrents.to/api/v1/search?q={requests.utils.quote(query)}&sort=seeders"
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        out = []
        for t in data.get("results", []):
            name = t.get("title", "")
            infohash = t.get("infohash", "").lower()
            if not infohash:
                continue
            magnet = (
                f"magnet:?xt=urn:btih:{infohash}"
                f"&dn={requests.utils.quote(name)}"
                f"&tr=udp://tracker.opentrackr.org:1337/announce"
            )
            size = _human_size(t.get("size", 0))
            out.append(_norm(name, size, t.get("seeders", 0),
                             t.get("leechers", 0), magnet, "SolidTorrents"))
        return out
    except Exception as e:
        return [{"error": f"SolidTorrents: {e}"}]


# ---------- Nyaa (anime) ----------
def search_nyaa(query):
    try:
        url = f"https://nyaa.si/?f=0&c=0_0&q={requests.utils.quote(query)}&s=seeders&o=desc"
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        out = []
        for row in soup.select("table.torrent-list tbody tr"):
            tds = row.find_all("td")
            if len(tds) < 7:
                continue
            a1 = tds[1].find_all("a")
            if not a1:
                continue
            name = a1[-1].get_text(strip=True)
            link = tds[2].find_all("a")
            magnet = ""
            for l in link:
                if l.get("href", "").startswith("magnet:"):
                    magnet = l["href"]
                    break
            if not magnet:
                continue
            size = tds[3].get_text(strip=True)
            seeders = tds[5].get_text(strip=True)
            leechers = tds[6].get_text(strip=True)
            out.append(_norm(name, size, seeders, leechers, magnet, "Nyaa", "anime"))
        return out
    except Exception as e:
        return [{"error": f"Nyaa: {e}"}]


# ---------- helpers ----------
def _human_size(n):
    if not n or n <= 0:
        return "?"
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def _cat_name(cat):
    return {
        "0": "all", "100": "audio", "200": "video", "300": "apps",
        "400": "games", "500": "porn", "600": "other",
    }.get(str(cat), "")


# ---------- aggregator ----------
SEARCHERS = {
    "tpb": search_tpb,
    "yts": search_yts,
    "bitsearch": search_bitsearch,
    "solid": search_solid,
    "nyaa": search_nyaa,
}


def search_all(query, sources=None, max_workers=8):
    """run all indexers in parallel, merge, dedupe by infohash, sort by seeders."""
    sources = sources or list(SEARCHERS.keys())
    all_results = []
    errors = []
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(SEARCHERS[s], query): s for s in sources if s in SEARCHERS}
        for fut in as_completed(futures):
            src = futures[fut]
            try:
                res = fut.result()
            except Exception as e:
                errors.append(f"{src}: {e}")
                continue
            for r in res:
                if "error" in r:
                    errors.append(r["error"])
                else:
                    all_results.append(r)

    # dedupe by infohash (extracted from magnet)
    seen = set()
    uniq = []
    for r in all_results:
        m = re.search(r"btih:([a-fA-F0-9]{40})", r["magnet"])
        h = m.group(1).lower() if m else r["magnet"]
        if h in seen:
            continue
        seen.add(h)
        uniq.append(r)

    uniq.sort(key=lambda x: x["seeders"], reverse=True)
    return uniq, errors