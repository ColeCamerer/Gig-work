# Gig System — Honest Strategy & Setup

This replaces the rosy economics in the original SETUP. Read it before you expect money.

## The real bottleneck

It is **not** producing the work — AI does that in minutes. The bottleneck is **getting a stranger with no reason to trust you to reply and pay.** Everything in these skills is built around two numbers:

1. **Reply rate** — % of pitches that get answered. This is the whole game.
2. **Not getting flagged** — if your account/email gets binned, reply rate is zero by definition.

## Realistic numbers (not the original doc's)

| Stage | Honest expectation |
|---|---|
| Reply rate, week 1, no reviews | 1–4% (so ~25–100 pitches per landed job) |
| Reply rate after 3–5 real reviews | 10–20% |
| Gigs/day actually worth pitching across all sources | a handful, not dozens |
| Month 1 earnings | $0–150 while you learn what lands |
| Month 2–3, if you stick with it | a few hundred/month, from real effort |

This is a **legit freelancing side-hustle accelerated by AI**, not passive income. People who treat it like a real service business make money. People who expect autopilot quit in week one with $0.

## The three things that actually move money

1. **Lead with proof.** Don't promise — show. A free one-sentence sample or a vivid logo concept in the pitch is the single biggest reply-rate lever. The applier does this by default; keep it on.
2. **Be early.** Pitch within ~30 min of a post. The scanner's loop mode + the qualifier's freshness scoring exist for this. A fast mediocre pitch beats a perfect late one.
3. **Get reviews.** The jump from 2% → 20% reply rate is reviews. Deliver genuinely good work, then ask. Three to five reviews changes the entire economics. The fulfiller reminds you to ask after every paid job.

## Don't get flagged — account setup

**Email (Craigslist):**
- Use an **aged Gmail** (weeks+ old, with some normal sent history). A fresh account blasting identical mail gets throttled same-day.
- Let the applier pace you (it caps daily sends, spaces them out, sends only in active hours, and never reuses a body). Don't override the caps to "send more" — that's the fast path to a dead account.
- Plain text, no links in first contact, no spammy words. The applier enforces this.

**Reddit:**
- You need an account with **some age and comment karma** before pitching, or r/forhire and r/slavelabour bots auto-remove you. Set `identity.reddit_username` in config.
- Read each sub's rules. Many require commenting in the thread (not DM), sometimes in a set format. Follow it exactly — breaking it = removed and possibly banned.
- One contact per poster. No DM-blasting.

## Honesty / positioning

Set `identity.positioning` in config:
- **`ai_assisted_disclosed`** (default, safer): sell "fast, AI-assisted, human-edited, same-day." Many clients want exactly this. No refund/trust risk.
- **`human`**: more replies, but you MUST stand behind the work and the fulfiller must edit it hard so it genuinely reads human.

Never fabricate reviews, credentials, or "years of experience." Fake social proof is what gets you reported and is not worth it.

## Quality is risk control

AI text and AI logos are increasingly detectable. An obvious-AI deliverable → refund/chargeback/bad review → dead young account. The fulfiller's Humanize pass and Quality gate are mandatory for this reason, not for polish. One bad review early can end the whole thing; one good review compounds.

## Folder structure

```
gigs/
  raw/  qualified/  applied/  delivered/
  samples/        ← drop a few of your best deliverables here to reuse as proof
  seen.txt        ← dedup
  config.json     ← all settings (sending caps, identity, targeting)
  reviews.md      ← log client reviews as you earn them (your reply-rate fuel)
logs/
  gig-log.md      ← all activity
  sent-today.log  ← enforces the daily send cap
```

## Daily flow

```
"scan for gigs"      → fresh hits to raw/
"qualify gigs"       → scored, scam-screened, top dozen kept
"apply to gigs"      → paced, personalized, proof-led pitches (caps enforced)
[wait for replies — check email/Reddit]
"they accepted: [paste reply]"  → fulfiller produces + humanizes + QA's the work
[send deliverable from the README, get paid]
"mark paid, ask for review"
```

Or `"scan every hour"` for loop mode so you catch gigs minutes after they post.

## Bottom line

It works if you run it like a real micro-business: be early, prove value, deliver genuinely good work, collect reviews, and let the pacing rules protect your accounts. It does not work as a get-rich button. Set expectations at "useful side income that grows," and you won't be disappointed.
