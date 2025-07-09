"""
pplx_fetcher.py  –  fetch URLs via Perplexity Sonar Search
----------------------------------------------------------
* Calls POST https://api.perplexity.ai/chat/completions
* Uses model "sonar" (search-grounded)
* Parses search_results[] → list[{title, url}]
"""

import os, json, requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("PPLX_API_KEY")
assert API_KEY, "⚠️  PPLX_API_KEY missing in .env"

PROMPT = (
    "Give me 25 English news or blog article URLs published within the last 7 days "
    "about Singapore's entertainment & content industries: gaming, OTT streaming, "
    "film, broadcast media, music, fashion IP, or tech media. "
    "Return only credible news/blog sources."
)

def fetch_pplx() -> list[dict]:
    url = "https://api.perplexity.ai/chat/completions"
    body = {
        "model": "sonar",              # search-enabled model
        "messages": [
            {"role": "user", "content": PROMPT}
        ],
        "temperature": 0.3,
        "top_p": 1,
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type":  "application/json",
    }

    r = requests.post(url, headers=headers, data=json.dumps(body), timeout=60)
    if r.status_code == 401:
        raise RuntimeError("401 Unauthorized → bad or inactive Perplexity API key.")
    r.raise_for_status()

    data = r.json()
    results = data.get("search_results", [])
    return [{"title": it["title"], "url": it["url"]} for it in results]

# CLI smoke-test
if __name__ == "__main__":
    links = fetch_pplx()
    print(f"Perplexity returned {len(links)} links")
    for art in links[:10]:
        print("•", art["title"])
