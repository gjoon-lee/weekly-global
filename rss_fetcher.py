"""
rss_fetcher.py  –  returns list[dict] of SG-content RSS items
-------------------------------------------------------------
* Reads feed URLs from feeds.txt
* Keeps items published in the last 7 days
* Filters by KEYWORDS in the title
* Designed to be imported (fetch_rss()) or run standalone
"""

from datetime import datetime, timedelta, timezone
import pathlib, requests, feedparser

# ── Config ──────────────────────────────────────────────
ROOT        = pathlib.Path(__file__).resolve().parent
FEEDS_FILE  = ROOT / "feeds.txt"
KEYWORDS    = ["gaming", "ott", "film", "movie", "music",
               "fashion", "broadcast", "ip", "media", "streaming"]
LOOKBACK_D  = 7
since_ts    = datetime.now(timezone.utc) - timedelta(days=LOOKBACK_D)

HDRS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/125 Safari/537.36 sg-content-bot"),
    "Accept": "application/rss+xml, application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://mothership.sg",        # fixes Mothership 403
}

# ── Helpers ─────────────────────────────────────────────
def kw_match(text: str) -> bool:
    t = text.lower()
    return any(k in t for k in KEYWORDS)

def best_date(entry):
    """Return datetime with tzinfo or None."""
    for attr in ("published_parsed", "updated_parsed"):
        if getattr(entry, attr, None):
            return datetime(*getattr(entry, attr)[:6], tzinfo=timezone.utc)
    return None

# ── Main function to import elsewhere ──────────────────
def fetch_rss() -> list[dict]:
    """
    Return list of {"title": str, "url": str}
    that pass date + keyword filters.
    """
    collected: list[dict] = []

    for raw in FEEDS_FILE.read_text(encoding="utf-8").splitlines():
        url = raw.strip()
        if not url or url.startswith("#"):
            continue

        try:
            resp = requests.get(url, headers=HDRS, timeout=20)
            resp.raise_for_status()
        except Exception:
            # print(f"!! HTTP fail → {url}  ({e})")
            continue

        fp = feedparser.parse(resp.content)
        if not fp.entries:
            continue

        for e in fp.entries:
            dt = best_date(e)
            if not dt or dt < since_ts:
                continue
            if not kw_match(e.title):
                continue
            collected.append({"title": e.title, "url": e.link})

    return collected


# ── Manual test hook ───────────────────────────────────
if __name__ == "__main__":
    articles = fetch_rss()
    print(f"Fetched {len(articles)} RSS articles")
    for art in articles[:10]:
        print("•", art["title"])
