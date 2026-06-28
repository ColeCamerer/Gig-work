---
name: gig-scanner
description: Scan Craigslist and Reddit (r/forhire, r/slavelabour, r/DesignJobs) gig boards for fresh text and design jobs that can be fulfilled with AI. Trigger when user says "scan for gigs", "find gigs", "check craigslist", "check reddit", "what gigs are up", or "run the scanner". Also trigger automatically at the start of a gig-working session.
---

# Gig Scanner

You find fresh, AI-solvable text and design gigs and hand them to the qualifier. Fresh is the operative word: a 20-minute-old post you can answer first is worth ten 8-hour-old ones. You surface; the qualifier scores.

## Setup

When invoked:
1. Read `/gigs/config.json` → `targeting` (cities, categories, reddit_subs, min_price, max_age_hours). Use defaults if missing.
2. Load `/gigs/seen.txt` (URLs already processed). Create if missing.
3. Scan Craigslist feeds + Reddit feeds (below), politely paced.
4. Apply freshness, price, keyword, and quick-scam filters.
5. Save new hits to `/gigs/raw/`, dedupe into seen.txt, log.

## Craigslist sources

| Category | Code | URL |
|---|---|---|
| Writing/Editing | wrg | `https://[city].craigslist.org/search/wrg?format=rss` |
| Creative | crg | `https://[city].craigslist.org/search/crg?format=rss` |
| Computer | cpg | `https://[city].craigslist.org/search/cpg?format=rss` |

Default cities: boston, newyork, chicago, losangeles, sfbay, seattle, austin, denver, atlanta, miami

### Scan script
```python
import urllib.request, xml.etree.ElementTree as ET, json, os, re, time, random
from datetime import datetime, timezone, timedelta

cfg = json.load(open("gigs/config.json")) if os.path.exists("gigs/config.json") else {}
t = cfg.get("targeting", {})
cities = t.get("cities", ["boston","newyork","chicago","losangeles","sfbay","seattle","austin","denver","atlanta","miami"])
categories = t.get("categories", ["wrg","crg","cpg"])
min_price = t.get("min_price", 30)
max_age_hours = t.get("max_age_hours", 12)

seen = set(open("gigs/seen.txt").read().splitlines()) if os.path.exists("gigs/seen.txt") else set()
hits, now = [], datetime.now(timezone.utc)

for city in cities:
    for cat in categories:
        url = f"https://{city}.craigslist.org/search/{cat}?format=rss"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                root = ET.fromstring(resp.read())
            for item in root.findall(".//item"):
                link = item.findtext("link") or ""
                if link in seen: continue
                title = item.findtext("title") or ""
                desc = re.sub(r'<[^>]+>', '', item.findtext("description") or "").strip()
                pub = item.findtext("{http://purl.org/dc/elements/1.1/}date") or item.findtext("pubDate") or ""
                pm = re.search(r'\$(\d+)', title + " " + desc)
                price = int(pm.group(1)) if pm else 0
                if price > 0 and price < min_price:
                    seen.add(link); continue
                hits.append({"url": link, "title": title, "description": desc, "price": price,
                             "city": city, "category": cat, "pubdate": pub,
                             "scraped_at": now.isoformat()})
                seen.add(link)
        except Exception as e:
            print(f"Error: {city}/{cat} — {e}")
        time.sleep(random.uniform(1.5, 4.0))  # polite pacing — don't hammer one host
```

**Pacing matters here too:** the `time.sleep` between fetches keeps you from looking like a scraper bot and getting the IP/account 403'd (which is exactly what a too-fast scan triggers). Don't remove it.

## Reddit sources

JSON feeds at `https://www.reddit.com/r/[sub]/new.json?limit=50`.

| Sub | Keep when |
|---|---|
| forhire | title starts with `[Hiring]` |
| slavelabour | title has `[Hiring]` or `[OFFER]` |
| DesignJobs | title has `[Hiring]` or `[Paid]` |

```python
subs = {
  "forhire": lambda x: x.lower().startswith("[hiring]"),
  "slavelabour": lambda x: "[hiring]" in x.lower() or "[offer]" in x.lower(),
  "DesignJobs": lambda x: "[hiring]" in x.lower() or "[paid]" in x.lower(),
}
for sub, keep in subs.items():
    try:
        req = urllib.request.Request(f"https://www.reddit.com/r/{sub}/new.json?limit=50",
                                     headers={"User-Agent": "gig-scanner/1.0 (personal use)"})
        data = json.load(urllib.request.urlopen(req, timeout=10))
        for c in data["data"]["children"]:
            p = c["data"]; title = p.get("title","")
            if not keep(title): continue
            link = "https://www.reddit.com" + p.get("permalink","")
            if link in seen: continue
            body = p.get("selftext","")
            pm = re.search(r'\$(\d+)', title + " " + body)
            price = int(pm.group(1)) if pm else 0
            if price > 0 and price < min_price: seen.add(link); continue
            hits.append({"url": link, "title": title, "description": body.strip()[:2000],
                         "price": price, "city": "reddit", "category": sub, "contact": "reddit_dm",
                         "pubdate": datetime.fromtimestamp(p.get("created_utc",0), timezone.utc).isoformat(),
                         "scraped_at": now.isoformat()})
            seen.add(link)
    except Exception as e:
        print(f"Error: reddit/{sub} — {e}")
    time.sleep(random.uniform(2.0, 5.0))
```

## Filters (apply to every hit)

**Freshness** — drop anything older than `max_age_hours` (default 12). Parse `pubdate`; if you can't, keep it but note unknown age. Tag hits posted <3h ago as fresh — these go to the top.

**Keywords** — keep only hits matching a target keyword:
- *Text:* blog, article, write, writing, copy, copywriting, content, social media, email, script, newsletter, description, product description, press release, bio, caption, post, proofread, edit, ghostwrite
- *Design:* logo, brand, branding, flyer, banner, graphic, brochure, business card, thumbnail, design, illustration, poster, ad creative, instagram, social graphic, icon, mockup

Classify TEXT or DESIGN by first match; if both, TEXT.

**Quick scam screen** — drop before saving (the qualifier does deeper screening, but catch the obvious here): titles/bodies pushing "weekly pay", "data entry", "personal assistant", "make $X/day", Telegram/WhatsApp-only contact, crypto, or "be your own boss". Log these as `SCAM-SKIP`.

**Repost screen** — if the title is near-identical to one already in seen.txt (same poster reposting daily), skip it; reposts convert poorly and pitching them repeatedly looks like spam.

## Saving raw hits

One JSON per hit to `/gigs/raw/`, filename `[timestamp]-[city]-[slug].json` (slug = first 4 title words, lowercased, hyphenated):
```json
{
  "id": "...", "status": "raw", "type": "TEXT|DESIGN",
  "url": "...", "title": "...", "description": "...",
  "price": 60, "price_stated": true,
  "city": "...", "category": "...", "contact": "email|reddit_dm",
  "fresh": true,
  "posted": "...", "scraped_at": "..."
}
```

## Dedup
Write all processed URLs to `/gigs/seen.txt`, one per line. Never save a listing twice.

## Logging
```
## [DATE TIME] SCAN
- Feeds checked: [N]  | New: [N]  | Text: [N]  | Design: [N]
- Fresh (<3h): [N]
- Skipped: seen [N], price [N], stale [N], scam [N], repost [N]
- Saved to raw: [N]
```

## After scanning
> "Scan complete — [N] new gigs ([T] text, [D] design), [F] fresh. Run `qualify gigs` to score them."

Then wait. Don't auto-qualify.

## Loop mode
If the user says "scan every hour" / "keep scanning": run, save, wait ~60 min (jittered), repeat. This is how you catch gigs while they're minutes old — the whole edge. Wake the user for any fresh gig priced $150+. Log each cycle.
