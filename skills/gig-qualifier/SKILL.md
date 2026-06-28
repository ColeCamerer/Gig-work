---
name: gig-qualifier
description: Score raw Craigslist and Reddit gigs and decide which are worth applying to. Trigger when user says "qualify gigs", "score gigs", "which gigs are worth it", "check the raw gigs", or after a scan completes.
---

# Gig Qualifier

You are the filter that protects your time and your reply rate. A gig is only worth a pitch if it's (1) fast AI-solvable, (2) pays enough, (3) clearly scoped, AND (4) actually winnable. Most gigs fail at least one. Cutting them is the job.

## Setup

When invoked:
1. List all files in `/gigs/raw/`. If empty: "No raw gigs to qualify. Run the scanner first."
2. Open each, read it, score it on 5 factors below.
3. Move winners to `/gigs/qualified/`, log rejections, discard the rest.
4. Report results sorted by score.

## Scoring (max 24)

### 1. AI Solvability (0–8)
Can this be done in <5 min with Claude/DALL-E, then human-edited, with no proprietary access?

| Pts | Criteria |
|---|---|
| 8 | Pure AI output + quick edit (blog post, logo, product copy, captions) |
| 6 | AI does 90%, minor formatting/export |
| 4 | AI does it but needs one custom input (their data, real photos) |
| 2 | Human effort >10 min |
| 0 | Human skill, in-person, or real credentials required |

**Auto-reject (kill it) if the listing has:** "ongoing"/"long-term", "portfolio required", "NDA", "interview", "trial project", "must be local", video/audio production, full app coding, or anything needing licensed medical/legal/financial advice.

### 2. Payout (0–6)
| Pts | Criteria |
|---|---|
| 6 | $100+ |
| 4 | $50–99 |
| 2 | $30–49 |
| 1 | Unstated (note: "ask for $X in pitch") |
| 0 | Under $30 |

### 3. Scope Clarity (0–4)
| Pts | Criteria |
|---|---|
| 4 | Crystal-clear deliverable ("500-word post on X") |
| 3 | Clear, minor assumptions |
| 2 | Vague but workable |
| 1 | Very vague — revision risk |
| 0 | No idea what they want |

### 4. Freshness (0–2)
Reply rate is mostly about being early.
| Pts | Criteria |
|---|---|
| 2 | Posted <3 hours ago |
| 1 | 3–8 hours |
| 0 | 8–12 hours (apply but low priority); over `max_age_hours` → reject as stale |

### 5. Winnability (0–4) — NEW, this is what stops wasted pitches
Can a no-review freelancer realistically land THIS one?

| Pts | Criteria |
|---|---|
| 4 | Small/individual client, casual post, low apparent competition, normal budget |
| 3 | Normal gig, some competition |
| 2 | Popular-looking post (big city wrg, lots of likely applicants) or slightly underpriced |
| 1 | High competition or client signals pickiness ("send 5 samples", "only experts") |
| 0 | **Scam / unwinnable** — see kill list below |

**Winnability auto-kill (score the gig 0 overall, do not apply):**
- Asks you to pay anything, buy supplies, or "pass a paid test"
- Wants bank/SSN/personal info up front, or pushes off-platform to Telegram/WhatsApp immediately
- "Weekly pay" / "data entry" / "personal assistant" mills (classic scams)
- Pay absurdly high for trivial work ($500 to copy-paste) = scam bait
- Pure reposts you've already seen (check repost signals)
- Crypto/MLM/"be your own boss" recruiting

## Threshold

| Score (of 24) | Decision |
|---|---|
| 16–24 | APPLY — strong, qualify |
| 12–15 | APPLY — decent, qualify |
| 8–11 | SKIP — marginal |
| 0–7 | REJECT |

Also respect `targeting.min_winnability_score` in config if set, and never qualify anything with a winnability auto-kill regardless of other scores.

## Focus the funnel

Don't qualify 30 gigs the applier can't get through. After scoring, if more than ~12 pass, keep only the **top 12 by score** in `/gigs/qualified/` and log the rest as "skipped — below cut line today." The applier's daily cap is small on purpose; feeding it your best dozen beats feeding it everything.

## Subtype enrichment

**TEXT:** BLOG_POST, PRODUCT_COPY, SOCIAL_CONTENT, EMAIL_COPY, SCRIPT, GENERAL_COPY
**DESIGN:** LOGO, BRAND_KIT, FLYER, SOCIAL_GRAPHIC, PRINT

## Qualified file format

Save to `/gigs/qualified/[same filename].json`:
```json
{
  "id": "...",
  "status": "qualified",
  "type": "TEXT",
  "subtype": "BLOG_POST",
  "url": "...",
  "title": "...",
  "description": "...",
  "price": 60,
  "price_stated": true,
  "score": 20,
  "score_breakdown": {"ai_solvability": 8, "payout": 4, "scope_clarity": 4, "freshness": 2, "winnability": 4},
  "why_apply": "...",
  "red_flags": [],
  "proof_idea": "One concrete sample line/concept to lead the pitch with",
  "estimated_time_minutes": 3,
  "fulfillment_notes": "...",
  "contact": "email | reddit_dm",
  "city": "...",
  "posted": "...",
  "qualified_at": "..."
}
```

Always fill `proof_idea` — the applier leads with it and it's the #1 reply driver.

## Rejection logging

For every rejected gig, one line in `/logs/gig-log.md`:
```
[DATE] REJECTED — [title] | Score: [X]/24 | Reason: [one sentence]
```
For scam kills specifically, prefix the reason with `SCAM:` so the pattern is searchable. Discard rejected gigs — don't save them anywhere.

## After qualifying

```
## Qualification complete

Processed: [N]
✅ Qualified: [N] (top [12] kept)
❌ Rejected: [N] (incl. [N] scams killed)

Top pick: "[title]" — [X]/24 | $[price] | [subtype] | proof: [proof_idea]

Run `apply to gigs` to pitch them (newest + highest first, paced).
```

## Price judgment for unstated gigs

Qualify well-scoped unstated-price gigs with a note to quote in the pitch:

| Job | Ask |
|---|---|
| Blog post (500–800w) | $60–90 |
| Product descriptions (5) | $50–70 |
| Logo (1 concept) | $90–125 |
| Social captions (10) | $50–60 |
| Email sequence (3) | $90 |
| Flyer | $60–85 |

(These are nudged up from rock-bottom — underpricing reads as low-quality and attracts the worst clients. Don't race to the floor.)
