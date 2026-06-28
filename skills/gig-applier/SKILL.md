---
name: gig-applier
description: Write and send pitches for qualified Craigslist and Reddit gigs without getting flagged. Trigger when user says "apply to gigs", "send pitches", "apply for the gigs", "pitch the gigs", or "write applications". Always trigger after qualification if user approves.
---

# Gig Applier

You write pitches that land replies and don't get the account banned. Two things kill this business: getting flagged as spam (so nothing arrives) and sounding like a template (so nothing gets answered). Everything below exists to prevent one of those two.

## The core rule

**One reply is worth more than fifty sends.** Do not spray. A small number of genuinely personalized, well-timed pitches beats mass-applying every time — and mass-applying is exactly what gets accounts killed. Quality and restraint ARE the optimization.

## Setup

When invoked:

1. Read config via `python3 scripts/gig.py status` (it loads config + secrets and shows remaining cap). Settings live in `/gigs/config.json`; real credentials live in `/gigs/secrets.json` (gitignored — never read/write secrets to config.json). These caps are hard limits, not suggestions.
2. Check remaining cap with `python3 scripts/gig.py cap` (date-aware — counts only today's sends from `gigs/sent-log.csv`, resets automatically). If it returns 0, **stop** and tell the user the cap is hit.
3. List `/gigs/qualified/` files with `"status": "qualified"`. Sort by `score` descending, then by freshness (newest `posted` first).
4. Work down the list, newest-and-best first, until the daily cap is reached. Leave the rest in `/gigs/qualified/` for the next run.
5. For each: write a unique pitch, send (or output draft), move to `/gigs/applied/`, log.

## Anti-flag rules (non-negotiable)

These are the difference between "delivered" and "the account is dead."

**Pacing**
- Never send two pitches back to back. Space them by a random gap between `min_minutes_between_sends` and `max_minutes_between_sends`.
- Only send during `active_hours_local`. Nobody legit applies to 8 gigs at 4am.
- Respect `max_applications_per_day` and `max_applications_per_source_per_day`. When in doubt, send fewer.

**Never reuse a body.** Craigslist and Gmail both fingerprint near-identical messages across recipients and bin them. Every pitch must be materially different in wording, structure, and length — not the same template with the name swapped. If you cannot make a pitch genuinely specific, skip that gig.

**Deliverability (email)**
- Plain text only. No HTML, no images, no signature graphics.
- **No links or attachments in the first message** (`no_links_in_first_contact`). Links in a cold reply are the #1 spam trigger. Offer the sample as text inline, or say "happy to send a link if useful."
- Avoid spam-trigger words: "guarantee", "100%", "free", "click here", "limited time", "act now", "cheap", "$$$", excessive exclamation points or ALL CAPS.
- Real subject line that threads to their post: `Re: [their exact title, trimmed]`.
- One recipient per email. Never CC/BCC multiple gigs.

**Account hygiene (tell the user once, then assume done)**
- Use an established Gmail (weeks old, with normal sent history), not a fresh burner — new accounts blasting identical mail get throttled immediately.
- Craigslist: don't reply to 10 posts in 5 minutes from one IP/account. The pacing rules above handle this.

## Reddit-specific rules

Reddit bans differently than email. For any gig with `"contact": "reddit_dm"`:

- **Check account readiness first.** If `identity.reddit_username` is empty, flag for the user: pitching from a brand-new, low-karma account gets auto-removed by subreddit bots. Account should have some age + comment karma.
- **Follow the subreddit's required format.** r/forhire and r/slavelabour often require you to comment in the thread (not just DM), and some require a specific template. If the post says "comment then DM" or "PM only," obey it exactly — breaking the rule = removed + possible ban.
- **Default flow:** post a short, specific public comment answering their need, then DM the fuller pitch only if comments are allowed. Never DM-blast.
- One pitch per poster. Don't comment AND spam-DM.

## Timing is reply rate

The single biggest controllable factor after personalization: **be early.** A pitch sent within ~30 min of posting massively outperforms one sent 8 hours later — the poster is still reading replies and hasn't picked someone. This is why the qualifier prioritizes fresh gigs and the scanner can run on a loop. When you have a fresh high-score gig, do it first.

## Writing the pitch

A pitch gets a reply when it proves you (a) actually read the post and (b) can do the specific thing, with the least friction to say yes. Structure:

1. **Specific opener** — reference a concrete detail from THEIR post (the product, the topic, a phrase they used, their business name). This is mandatory and must be unique per gig. Generic openers get deleted.
2. **Proof, not promise** — this is the highest-leverage line. Instead of "I do this regularly," show a sliver of the actual work: one sample sentence in their voice, a one-line angle for their blog, a described logo direction. Lead with value. (See "Lead with proof" below.)
3. **Frictionless close** — one easy question or a clear next step. Make saying yes a two-word reply.

Constraints:
- Under ~90 words. Shorter reads as confident and human.
- Lowercase "hey" opener. No "Dear", no "I hope this finds you well", no corporate voice.
- Vary it. Don't open every pitch the same way. Vary sentence length and rhythm.
- Match `identity.positioning` (see below).

### Lead with proof (do this whenever possible)

The pitch that wins isn't "I can write your blog post" — it's giving them a taste so they see quality before they reply:

- **BLOG_POST / copy:** include one strong sample sentence or the headline + first line you'd use, in their tone.
- **PRODUCT_COPY:** write one of their product descriptions right there in the pitch (pick the scent/item from their post).
- **SOCIAL_CONTENT:** drop one finished caption as a sample.
- **LOGO / design:** describe the exact concept in vivid detail (shape, palette, feel) so they can picture it; offer to send a concept.

A free micro-sample costs you 30 seconds and is the difference between 2% and 15% reply rate. Worth it every time on high-score gigs.

## Positioning (honesty setting)

Read `identity.positioning`:

- **`ai_assisted_disclosed`** — Position as fast, AI-assisted, human-edited. Many clients actively want this (cheap, fast, good enough). Frame it as a feature: "I use AI-assisted drafting and edit every line myself, so turnaround is same-day." No refund/trust risk. This is the default and the safer long-term play.
- **`human`** — Present as a normal freelancer. More replies, BUT the fulfiller MUST edit the work hard so it genuinely reads human, and you must stand behind quality. Do not claim credentials you don't have. Never lie about being local, certified, etc.

Either way: **never** invent fake reviews, fake client names, or fake credentials. That's what gets you reported.

## Pitch patterns (starting points — personalize every time)

These are skeletons. The bracketed parts are where the real, specific work goes. Never send one unmodified.

**BLOG_POST / GENERAL_COPY (with proof)**
```
Subject: Re: [their title]

hey,

[specific reference to their topic/site]. quick angle off the top: "[one real sample headline or opening line in their tone]" — that's the kind of thing i'd run with.

can have the [word count] done by [timeframe], casual like you said. want me to send the full draft on spec so you only pay if you like it?

— [name]
```

**PRODUCT_COPY (with proof)**
```
Subject: Re: [their title]

hey,

took a swing at one of yours so you can see the feel:

"[one finished ~80-word product description for an item from their post]"

if that's the vibe i can knock out the other [N] today. want me to?

— [name]
```

**SOCIAL_CONTENT (with proof)**
```
Subject: Re: [their title]

hey — [reference their niche]. sample so you're not guessing:

"[one finished caption with 2-3 real hashtags]"

i can do all [N] in that energy today. good to go?

— [name]
```

**LOGO / DESIGN (vivid concept)**
```
Subject: Re: [their title]

hey,

[business name] — love it. picturing [specific concept: shape/mark], in [their palette], [feel], no [thing they said to avoid]. clean on a sign and tiny on instagram.

can send a concept in 24h, revise from there. want to see it?

— [name]
```

## Sending (email)

If SMTP has real values in `/gigs/config.json` (not the `your@gmail.com` placeholder):

```python
import smtplib, json, time, random
from email.mime.text import MIMEText

with open("gigs/config.json") as f:
    cfg = json.load(f)
smtp = cfg["smtp"]

# plain text only, no attachments, no links in first contact
msg = MIMEText(body, "plain")
msg["From"] = f'{smtp["from_name"]} <{smtp["from_email"]}>'
msg["To"] = reply_address
msg["Subject"] = subject

with smtplib.SMTP_SSL(smtp["host"], smtp["port"]) as server:
    server.login(smtp["username"], smtp["password"])
    server.send_message(msg)
```

Between sends, wait a randomized gap (don't actually `sleep` for 40 min in one run — instead, send what the gap allows, then tell the user "next batch in ~X min" or rely on loop mode).

**If SMTP is placeholder/unset:** output each pitch inline as a ready-to-paste draft with the destination, and tell the user to add a real Gmail app password to auto-send and pace next time.

## Extracting the reply address (Craigslist)

Fetch the listing page and look for the anonymized reply address:

```python
import urllib.request, re

def get_reply_address(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=8) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
    m = re.search(r'[\w\.\-]+@[\w\.\-]*craigslist\.org', html)
    if m: return m.group(0)
    m = re.search(r'[\w\.\-]+@[\w\.\-]+\.\w+', html)
    return m.group(0) if m else None
```

If it's a web form instead of email, flag it for manual send — don't try to auto-submit forms (that's bot behavior that gets flagged).

## Saving applied gig

Update the gig file and move to `/gigs/applied/`:

```json
{
  "status": "applied",
  "pitch_sent": "...(full text)...",
  "sent_to": "abc123@hb.craigslist.org",
  "sent_at": "...",
  "send_method": "smtp | manual | reddit_comment | reddit_dm",
  "followup_due": "...(sent_at + one_followup_after_hours)...",
  "followups_sent": 0
}
```

## Logging

After each send, record it two ways:
- The cap counter + ledger:
  `python3 scripts/gig.py log pitched --channel [craigslist|reddit|fiverr] --lane [LANE] --title "[title]" --price [price]`
  and `python3 scripts/_config.py`-backed `record_sent` is called by the cap flow — simplest is to also append the destination so duplicates are caught.
- Human-readable line in `/logs/gig-log.md`:
  `[DATE] APPLIED — [title] | $[price] | [email/reddit] | Method: [..] | Proof: [yes/no]`

Logging `pitched` to the ledger is what lets metrics/learn see every channel (incl. Fiverr/Reddit inbound), not just outbound email.

## Follow-ups

One polite follow-up, once, after `one_followup_after_hours`, only if no reply:
```
hey, just bumping this in case it got buried — still happy to [deliverable] if the spot's open.
```
After one follow-up with no reply, stop. Two+ follow-ups is harassment and gets you reported. Mark the gig dead.

## Duplicate protection

Before sending, check `/gigs/applied/` and `/logs/sent-today.log` for the same `sent_to` or `url`. Never pitch the same poster twice. Never re-pitch a listing you've already contacted.

## After applying

```
## Applications sent ([N] today, cap [max])

✅ Sent:
- "[title]" → [dest] ($[price]) [proof sample included]

⚠️ Manual send needed:
- "[title]" → [reason: web form / reddit account not ready] — [url]

⏸️ Held for next run (cap reached): [N] gigs still in /gigs/qualified/

Follow-ups due: [list any] | Watch for replies, run `fulfill gig [name]` when one lands.
```

## Checking for replies

You can't watch email unless Gmail MCP is connected. If it is, scan for replies from gig addresses and surface them. Otherwise tell the user to check manually and paste the reply into the fulfiller.
