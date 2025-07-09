"""
newsapi_fetcher.py  —  stricter SG-content filter
"""

from datetime import datetime, timedelta
import os, requests, urllib.parse, re
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("NEWSAPI_KEY")
assert API_KEY, "NEWSAPI_KEY missing"

# ------- config you can tweak -------
KEYWORDS  = ["gaming", "ott", "streaming", "film", "movie",
             "music", "fashion", "broadcast", "ip", "media"]
DOMAINS   = ",".join([
    "channelnewsasia.com",
    "asiaone.com",
    "mothership.sg",
    "straitstimes.com",
    "hardwarezone.com.sg",
])
EXCLUDE   = ['singapore dollar', 'stock', 'finance']
DAYS      = 7
# ------------------------------------

today  = datetime.utcnow().date()
from_d = today - timedelta(days=DAYS)

def build_query() -> dict:
    """Return dict of query params for NewsAPI."""
    kw_title = " OR ".join(f'"{k}"' for k in KEYWORDS)
    exclude  = " ".join(f'-"{e}"' for e in EXCLUDE)
    return {
        "qInTitle": f"{kw_title} AND singapore {exclude}",
        "from":     from_d.isoformat(),
        "language": "en",
        "sortBy":   "publishedAt",
        "pageSize": 100,
        "domains":  DOMAINS,
        "apiKey":   API_KEY,
    }

# post-filter regex to double-check
KW_RE = re.compile("|".join(KEYWORDS), re.I)

def fetch_newsapi() -> list[dict]:
    params = build_query()
    url = "https://newsapi.org/v2/everything?" + urllib.parse.urlencode(params)
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if data.get("status") != "ok":
        raise RuntimeError(data)

    clean = []
    for art in data["articles"]:
        title = art["title"] or ""
        if KW_RE.search(title):        # secondary safeguard
            clean.append({"title": title, "url": art["url"]})
    return clean

# CLI test
if __name__ == "__main__":
    items = fetch_newsapi()
    print(f"NewsAPI returned {len(items)} filtered items")
    for a in items[:10]:
        print("•", a["title"])
