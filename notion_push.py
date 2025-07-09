"""
notion_push.py — single function to add a row to Notion DB
"""

import os
from notion_client import Client
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("NOTION_TOKEN")
DB_ID = os.getenv("NOTION_DB_ID")
assert TOKEN and DB_ID, "✘ NOTION_TOKEN / NOTION_DB_ID missing in .env"

client = Client(auth=TOKEN)

# ----------  pull all existing URLs ONCE  -----------------
def get_existing_urls() -> set[str]:
    urls = set()
    has_more = True
    cursor = None

    while has_more:
        resp = client.databases.query(
            **{
                "database_id": DB_ID,
                "start_cursor": cursor,
                "page_size": 100,
                "filter": {      # only rows that actually have a URL
                    "property": "URL",
                    "url": {"is_not_empty": True}
                },
                "sorts": [{"timestamp": "created_time", "direction": "descending"}],
            }
        )
        for page in resp["results"]:
            prop = page["properties"].get("URL")
            if prop and prop["url"]:
                urls.add(prop["url"])
        has_more = resp["has_more"]
        cursor   = resp.get("next_cursor")
    return urls


# ----------  conditional push -----------------------------
def push(article: dict, existing: set[str]) -> bool:
    """
    Insert article if its URL not in `existing`.
    Returns True if inserted, False if skipped.
    """
    if article["url"] in existing:
        return False   # duplicate → skip

    client.pages.create(
        parent={"database_id": DB_ID},
        properties={
            "Name":    {"title": [{"text": {"content": article["title"]}}]},
            "URL":     {"url": article["url"]},
            "Summary": {"rich_text": [{"text": {"content": article["summary_md"]}}]},
        }
    )
    existing.add(article["url"])   # update cache
    return True
