"""
gather_links.py
---------------
Combine RSS + NewsAPI, dedup on URL, print count & titles.
"""

import rss_fetcher, newsapi_fetcher, pplx_fetcher, judge, summarise, time, notion_push

# ---- Dedup helper -------------------------------------
def dedup(items: list[dict]) -> list[dict]:
    seen, out = set(), []
    for it in items:
        if it["url"] not in seen:
            seen.add(it["url"])
            out.append(it)
    return out

# ---- Main ---------------------------------------------
def main():
    print("📡 Fetching RSS ...")
    rss_links   = rss_fetcher.fetch_rss()
    print(f"  → {len(rss_links)} items")

    print("📰 Fetching NewsAPI ...")
    news_links  = newsapi_fetcher.fetch_newsapi()
    print(f"  → {len(news_links)} items")

    print("🔎 Fetching Perplexity ...")
    pplx_links = pplx_fetcher.fetch_pplx()
    print(f"  → {len(pplx_links)} items")

    all_links   = dedup(rss_links + news_links + pplx_links)
    print(f"\n✅ Total unique links: {len(all_links)}\n")

    print("\n🤔 Running GPT relevance judge ...")
    kept = []
    for art in all_links:
        if judge.judge_article(art["url"], art["title"]):
            kept.append(art)
    print(f"  → kept {len(kept)} of {len(all_links)} links")

    # Show first 20 titles as a sanity check
    for art in kept[:20]:
        print("✔", art["title"])

    print("\n📝 Generating Korean summaries ...")
    summaries = []
    for art in kept:
        art["summary_md"] = summarise.summarise(art["url"])
        summaries.append(art)
        time.sleep(0.3)   # polite pacing
    print(f"  → summarised {len(summaries)} articles")

    print("\nPreview first summary:\n")
    print(summaries[0]["summary_md"])
    
    print("\n📤 Sending to Notion …")
    existing_urls = notion_push.get_existing_urls()
    added = 0
    
    for art in summaries:
        if notion_push.push(art, existing_urls):
            added += 1
            time.sleep(0.3)        # be polite to Notion API
    print(f"✅  Added {added} new rows (skipped {len(summaries)-added} duplicates).")


if __name__ == "__main__":
    main()
