---
name: gig-closer
description: Turn a client reply into a paid, agreed job — handle questions, scope, price negotiation, and payment terms without losing the deal or getting scammed. Trigger when a client replies but hasn't fully accepted: "they replied", "client asked about price", "they want to negotiate", "how do I respond", "close this gig", or when a reply is detected that isn't a clean yes.
---

# Gig Closer

A reply is not a sale. Most money leaks in the gap between "interested" and "paid" — the client asks a question, haggles, goes quiet, or tries to move off-platform. Your job is to close that gap fast, warmly, and safely, then hand a clean agreed job to the fulfiller.

## Read the reply first

Classify what kind of reply it is, then respond to that:

| Reply type | What they're really doing | Your move |
|---|---|---|
| **Soft yes** ("sounds good, send it") | Ready, just needs the path | Confirm scope + price + terms in one short message, then deliver |
| **Question** (timeline? samples? can you do X?) | De-risking | Answer crisply, then ask the one question that moves to yes |
| **Price push** ("can you do it cheaper?") | Testing | Hold value, offer a smaller scope at their number — not a discount on the same scope |
| **Vague interest** ("maybe, tell me more") | Not sold | Send a free micro-sample. Proof closes what promises can't |
| **Scope creep** (wants more than posted) | Opportunity | Say yes and re-quote up — more work = more money |
| **Scam signal** (see below) | Trying to use you | Disengage. No deal is better than a scam |

## Close fast, stay human

- Reply within minutes when you can — speed keeps you top of mind while they're still deciding.
- Keep it short, lowercase-friendly, no corporate voice. Same human tone as the pitch.
- Always end with one clear next step or a single question. Never leave it open-ended.
- Confirm three things before any work starts: **exact deliverable, price, and payment method/timing.** Ambiguity here is where disputes come from.

## Handling price negotiation (don't race to the floor)

- Never just drop the price for the same work — it signals the first number was fake and invites more pushing.
- Trade scope for price: "I can do 400 words instead of 600 for $X" or "one concept instead of two."
- Anchor on value and speed: "I can have it done today" is worth more than $10 off.
- Know your floor from `catalog.json` pricing; below it, politely pass — a $10 job that eats an hour of back-and-forth loses money.

## Payment terms (protect yourself without friction)

- Small jobs (≤ ~$75): deliver, then payment on receipt is usually fine and lowers friction.
- Bigger jobs (> ~$75 or multi-part): **50% up front, 50% on delivery.** State it plainly and friendly.
- Accept only what's in `identity.payment` (PayPal/Venmo). Send your handle; don't ask for theirs.
- For text/design, you can deliver a **watermarked or low-res preview** first on larger jobs, full files on payment. Honest and standard practice.

## Scam / safety screen (disengage if any appear)

- Wants to pay by check, gift card, or "overpayment then refund the difference" → classic scam, walk away.
- Pushes to move to Telegram/WhatsApp immediately, or wants personal/banking info → walk away.
- Sends a "deposit" link for you to click, or asks you to buy software/supplies first → walk away.
- Offer is wildly overpriced for trivial work → bait, walk away.
- Trust the qualifier already screened the listing; the closer is the second gate when talking to a human.

## Response templates (personalize every time)

**Soft yes → lock it:**
```
great — so that's [exact deliverable] for $[price], and i'll have it to you [timeframe].
i take [PayPal/Venmo] — want me to send it over once you've had a look, or do half up front?
send me [the one input you need] and i'll start now.
```

**Question (samples/timeline):**
```
yep — [direct answer]. i can have it done [timeframe].
want me to send a quick sample first so you're not guessing? just need [one input].
```

**Price push:**
```
i hear you. at $[their number] i'd do [reduced scope] instead of [full] — still solid, just tighter.
or for the full [deliverable] i can hold $[your price] and have it today. which works?
```

**Vague interest → sample close:**
```
here's a quick taste so you can see the fit:
"[one real sample line/concept for their job]"
if that's the vibe i can do the whole thing by [timeframe]. want me to?
```

## Handoff to fulfiller

Once they've agreed deliverable + price + terms:
1. Update the gig file in `/gigs/applied/` (or wherever it lives): set `status: "accepted"`, add `agreed_price`, `agreed_scope`, `payment_terms`.
2. Trigger the fulfiller to produce the work.
3. Log: `[DATE] CLOSED — [title] | $[agreed] | terms: [..]` and append a `REPLIED` line if not already logged (so metrics/learn count the reply).

## After closing

```
✅ Closed: "[title]" — $[agreed] for [scope], [terms].
→ Producing the deliverable now (fulfiller).
[or] ⚠️ Sent counter/sample, waiting on their reply.
[or] 🚫 Walked away — [scam/too-low], logged.
```

## The long game

Every closed job is a review opportunity and a possible repeat client. Close warm, deliver fast, and the same person comes back without you pitching again — repeat clients are the cheapest income in the whole system.
