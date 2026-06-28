---
name: gig-fulfiller
description: Produce the deliverable for an accepted Craigslist/Reddit gig, edited so it reads human and passes a quality bar. Trigger when user says "fulfill [gig]", "complete the job", "do the work", "they accepted", "got a reply", or pastes a client brief/acceptance.
---

# Gig Fulfiller

You produce the deliverable AND make it good enough that the client pays, doesn't ask for a refund, and might leave a review. A raw AI draft is not the deliverable — the edited, human-reading, on-brief version is. The reputation you build here is what makes the money compound.

## Setup

1. Ask: "Which gig was accepted? Paste their reply or give me the job name."
2. Find the file in `/gigs/applied/` (or use what they paste).
3. Read `type`/`subtype` to pick the path, and re-read the original listing for every detail.
4. Produce the draft → run the **Humanize pass** → run the **Quality gate**. Only then save.
5. Save to `/gigs/delivered/[job-id]/`, tell the user how to send it.

## Why this matters (read once)

Clients increasingly spot AI text and AI logos. An obvious-AI deliverable gets: refund requests, chargebacks, public bad reviews, and on Reddit/Craigslist, reports. One bad review on a young account can end the whole operation. So the editing pass below is not optional polish — it's risk control.

## Routing

| Subtype | Path |
|---|---|
| BLOG_POST, PRODUCT_COPY, SOCIAL_CONTENT, EMAIL_COPY, SCRIPT, GENERAL_COPY | Text path |
| LOGO, BRAND_KIT | Design path → image + spec |
| FLYER, SOCIAL_GRAPHIC, PRINT | Design path → image + spec |

---

## TEXT PATH

### Extract first
Topic, length, tone, audience, keywords, any examples they linked, restrictions. If something critical is missing and the client hasn't said, make a reasonable assumption and note it — don't bounce trivial questions back to them.

### Write to standard
| Subtype | Length | Notes |
|---|---|---|
| BLOG_POST | as specified, default 600w | H2 subheads, no filler intro, get to the point |
| PRODUCT_COPY | ~80–100w each | feature → benefit, soft CTA |
| SOCIAL_CONTENT | 50–150w each | platform-appropriate, 2–4 real hashtags |
| EMAIL_COPY | ~200w each | subject line + one clear CTA |
| SCRIPT | ~150w per video minute | hook in first 5s, written for the ear |
| GENERAL_COPY | as specified | match their tone exactly |

### Humanize pass (MANDATORY — run on every text deliverable)

After the first draft, edit specifically to remove AI tells. This is the step that prevents refunds.

**Delete these phrases on sight:** "In conclusion", "In today's world/fast-paced world", "It's worth noting", "Delve into", "navigate the landscape", "unlock/unleash", "elevate", "game-changer", "when it comes to", "at the end of the day", "moreover/furthermore/additionally" stacked together, "whether you're a X or a Y".

**Fix the rhythm.** AI writes uniform medium sentences. Humans don't. Break it up: a three-word sentence next to a long one. Start a sentence with "And" or "But" occasionally. Cut every sentence that's just restating the previous one.

**Add specificity.** Vague = AI. Replace "a popular option" with the actual product name. Replace "many people" with a concrete example. Specifics are what a real expert writes and what AI omits.

**Kill the symmetry.** AI loves perfect parallel lists and "Firstly/Secondly/Thirdly". Make lists uneven and natural. Vary how sections open.

**Read it aloud in your head.** If a line sounds like a brochure or a press release, rewrite it the way a person would actually say it.

### Output
`/gigs/delivered/[job-id]/deliverable.md`, with a header:
```
# Deliverable: [title]
Client: [ref]
Produced: [date]
Notes: [assumptions made]
---
```
Then the content.

### Quality gate (must pass all before saving)
- Length within 10% of what they asked?
- Zero phrases from the delete list above?
- Sentence rhythm varied (not all medium-length)?
- On their stated tone and audience?
- At least 2–3 concrete specifics (names, numbers, real examples)?
- **Would you pay $[price] for this as the client?**

If any answer is no, fix that part. Don't save mediocre work — mediocre work is how the account dies.

### Red-team review (separate pass — do NOT skip)

The quality gate above is graded by the same mind that wrote the piece, so it has blind spots. Run a second, distinct pass with a hostile lens before saving:

> Re-read the deliverable as a skeptical client who is *looking for a reason not to pay.* Where is it generic? Where does it sound AI? What did they ask for that's missing or thin? What would make them request a revision?

Write down the 2–3 weakest points that pass finds, fix them, then save. This is a fresh critical read, not a re-skim — if you can, treat it as a different reviewer than the writer. It's the cheapest insurance against a refund or a bad review on a young account.

---

## DESIGN PATH

### Build the prompt
From the listing: style direction, industry, color direction, and what to avoid. **Never put text inside the logo** — DALL-E/most models render text badly and it's the #1 tell of an AI logo. Generate the mark only; text gets added cleanly in Canva.

Example:
```
A modern minimal logo mark for a neighborhood bakery. Abstract shape suggesting wheat and warmth. Wheat-gold, cream, soft-brown palette. Clean vector-style lines, no text, works on a sign and small on instagram. Warm, upscale, no cartoon mascot.
```

### Generate (if OPENAI_API_KEY set)
```python
import openai, urllib.request, os
client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
r = client.images.generate(model="dall-e-3", prompt=prompt, size="1024x1024", quality="hd", n=1)
urllib.request.urlretrieve(r.data[0].url, f"gigs/delivered/{job_id}/logo-v1.png")
```

### Design quality gate
- No garbled text in the image (regenerate if any letters appear)?
- Matches their stated palette and style?
- Readable/clean when shrunk to thumbnail size?
- Not a generic clip-art look?

If it fails, adjust the prompt and regenerate before delivering. Deliver a concept you'd be proud to put your name on.

### Always include `design-spec.md`
Colors (hex), font suggestions, usage notes, and Canva recreation steps + where to add the text. This makes the deliverable look professional even when the image is one concept, and gives the client real value.

### If no OPENAI_API_KEY
Output the finished prompt + full spec and tell the user to paste it into DALL-E/Midjourney/Firefly, then drop the image in the folder. Still a usable deliverable.

---

## Delivered folder
```
/gigs/delivered/[job-id]/
  deliverable.md      (text)
  logo-v1.png         (design)
  design-spec.md      (design)
  README.md           (how to send + client message + payment)
```

### README.md always
```markdown
# How to Deliver: [title]
## What's in this folder
- [file]: [what]
## How to send
[specific steps]
## Suggested message to client
---
hey, here's the [deliverable] — [one specific line about it]. let me know if you want any tweaks.
payment whenever you're set — [paypal/venmo from config].
— [name]
---
## Payment
- Amount: $[price] via [method]
- Polite nudge if not paid 48h after they confirm.
```

Pull the payment handle from `identity.payment` in config. Don't put payment links in the deliverable files themselves beyond the README.

## Update + log
Move a copy of the gig JSON to `/gigs/delivered/[job-id]/gig.json` with:
```json
{"status": "delivered", "delivered_at": "...", "delivered_path": "...", "fulfillment_time_minutes": N, "notes": "..."}
```
Log to the ledger (so all channels feed metrics/learn) and the human log:
```
python3 scripts/gig.py log delivered --channel [..] --lane [LANE] --title "[title]" --price [price]
```
```
[DATE] DELIVERED — [title] | $[price] | [subtype] | [N] min | [path]
```

## After delivering
> "Done — deliverable at `/gigs/delivered/[job-id]/`, edited to read human and quality-checked. Copy the message from the README and send. Expecting $[price]. Mark paid when confirmed, and if they're happy, ask for a quick review — that's what raises your reply rate next time."

## Revisions
Client asks for changes → re-read original, change only what they asked, save as `-v2`, update README. Fast, gracious revisions are how you turn a one-off into a repeat client and a review.

## After payment: log it + ask for the review
When the user confirms payment, log it (`python3 scripts/gig.py log paid --channel [..] --lane [LANE] --title "[title]" --price [amount]`) — this is what makes $/pitch and earnings real in the dashboards. Then prompt the user to ask the client for a short review/testimonial. Three to five real reviews is the single thing that takes reply rate from ~2% to ~20%. Track collected reviews in `gigs/reviews.md` to reuse (with permission) as social proof later.
