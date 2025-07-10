"""
deepresearch_fetcher.py  –  fetch URLs via OpenAI “o3-deep-research”

* Uses the new Deep Research endpoint (client.responses.create)
* Asks for 25 links published in the last 7 days that match your vertical
* Parses the citations that the model returns
* Falls back to simple regex if the model prints a bullet list instead
"""

from __future__ import annotations
import os, re
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError         

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
assert client.api_key, "⚠️  OPENAI_API_KEY missing in .env"

PROMPT = (
    "Give me 25 ENGLISH news- or blog-article titles with their URLs, "
    "all published *within the last 7 days*, about Singapore’s entertainment "
    "& content industries (gaming, OTT streaming, film, broadcast, music, "
    "fashion IP, tech media). Credible sources only, no paywalled or SEO spam."
)

def _parse_bullets(text: str) -> list[dict]:
    """Fallback extractor for ‘- Title — https://…’ lines."""
    links: list[dict] = []
    pat = re.compile(r"[-*\d.\s]*\s*(.+?)\s+[—\-–]\s+(https?://\S+)")
    for line in text.splitlines():
        m = pat.match(line.strip())
        if m:
            links.append({"title": m.group(1).strip(), "url": m.group(2)})
    return links

def fetch_deepresearch() -> list[dict]:
    """Return `[{"title": str, "url": str}]`."""
    try:
        resp = client.responses.create(
            model="o3-deep-research-2025-06-26",          # alias “o3-deep-research”
            input=[{
                "role": "developer",
                "content": [{"type": "input_text", "text": PROMPT}]
            }],
            #reasoning={"summary": "auto"},
            tools=[{"type": "web_search_preview"}],
            # optional: background=True  → async, poll with task_id
        )

        final = resp.output[-1].content[0]               # easiest handle
        # ① Preferred: grab the structured citations
        if getattr(final, "annotations", None):
            return [
                {"title": a.title, "url": a.url}
                for a in final.annotations
                if a.url.startswith("http")
            ]

        # ② Fallback: scrape the plain-text bullet list
        return _parse_bullets(final.text)

    except OpenAIError as e:
        print("Deep Research fetch failed:", e)
        return []

# quick CLI smoke-test
if __name__ == "__main__":
    arts = fetch_deepresearch()
    print("Deep Research returned", len(arts), "links")
    for a in arts[:10]:
        print("•", a["title"])
