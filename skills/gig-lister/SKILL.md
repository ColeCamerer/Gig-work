---
name: gig-lister
description: Generate ready-to-post inbound service listings (Fiverr gigs, Craigslist services ads, Reddit [FOR HIRE]/[OFFER] posts) so buyers come to you instead of you cold-pitching. Trigger when user says "create listings", "make my fiverr gigs", "post my services", "set up inbound", "list my services", or "go passive".
---

# Gig Lister (Inbound)

Cold pitching is outbound and capped by reply rate. This skill builds the **inbound** side: standing, productized offers buyers find and order on their own. It's the closest the system gets to passive income — set once, earns repeatedly. Use it alongside the outbound pipeline, not instead of it.

## What it produces

For each service the user can deliver (writing, copy, logos, social, etc.), generate platform-tuned listings saved to `/gigs/listings/[platform]/`:

- **Fiverr** — gig title, search tags, packages (Basic/Standard/Premium), description, FAQ, requirements
- **Craigslist services** — ad title + body for the relevant `services` category (not gigs)
- **Reddit** — a `[FOR HIRE]` (r/forhire) and `[OFFER]` (r/slavelabour) post, formatted to each sub's rules

The user posts these manually (these platforms ban scripted posting — see Guardrails). Set-once, inbound-forever.

## Source of truth: the catalog

Pull lanes, deliverables, pricing tiers, and keywords from `gigs/catalog.json` — it's the single source of truth for what this business offers (19 lanes and counting). Don't hardcode services here; read the catalog and build listings for whichever lanes the operator is currently pushing. Adding a new lane to the catalog automatically makes it listable.

## Productize first

Inbound only works if the offer is a concrete product with a price, not "I do writing." Define tight packages from the catalog's `pricing` tiers (tune to `identity` and local rates):

| Product | Basic | Standard | Premium |
|---|---|---|---|
| Blog posts | 1 × 600w, $35 | 3 × 600w, $90 | 5 × 800w + SEO, $175 |
| Product descriptions | 5 × 100w, $40 | 10, $70 | 20 + SEO keywords, $130 |
| Social captions | 10 captions, $35 | 20 + hashtags, $60 | 30 + 1-week schedule, $90 |
| Logo | 1 concept, $45 | 2 concepts + revisions, $90 | full mini brand kit, $175 |
| Email copy | 1 email, $40 | 3-email sequence, $95 | 5-email + subject A/B, $160 |

Price the **Basic of your first listing deliberately low** until you have 3-5 reviews — the first reviews are worth more than the first dollars. Raise prices once reviews land.

## Positioning

Honor `identity.positioning`:
- `ai_assisted_disclosed` → "Fast, AI-assisted and human-edited — same-day delivery, you only pay if you're happy." Many buyers filter FOR this.
- `human` → standard freelancer voice; deliverables must be edited to read fully human.

Never fake reviews, order counts, or credentials. On Fiverr especially, fake engagement = permanent ban.

## Platform templates

### Fiverr gig
```
Title: I will write a [SEO blog post / 5 product descriptions / ...] in 24 hours
Search tags: [5 tags Fiverr buyers actually search: "blog writing", "seo article", "product description", "copywriting", "content writer"]
Category: Writing & Translation > [subcategory]

[Gig description — 2 short paras: the outcome they get + why fast/reliable.
Lead with benefit, not "I am passionate". Plain, confident, specific.]

Packages:
- Basic ($X): [exact deliverable, delivery days, revisions]
- Standard ($Y): [more]
- Premium ($Z): [most]

FAQ:
- Turnaround? Same/next day on Basic.
- Revisions? [n] included.
- What do you need from me? [the brief inputs]

Requirements (buyer fills at order): topic, tone, audience, keywords, examples.
```

### Craigslist services ad
```
Section: services > [creative (crs) / writing (wrs) / computer (cps)]
Title: Same-Day Blog Posts & Web Copy — $35+ (fast, clean, edited)

[3-4 plain sentences: what you do, turnaround, price entry point, how to
contact. No links in the first version — CL flags link-heavy service ads.
One clear call: "Email me your topic and I'll send a sample."]
```

### Reddit [FOR HIRE] (r/forhire)
```
Title: [FOR HIRE] Fast blog posts, product copy & logos — same-day, from $35

Body:
- What I do: [bullet list of products + prices]
- Turnaround: same/next day
- Samples: [point to portfolio_url or "DM and I'll send one free"]
- Payment: PayPal/Venmo, [release terms]
- [If positioning=ai_assisted_disclosed, say so honestly here]

Follow r/forhire rules: [FOR HIRE] tag, one post per ~24-48h, real prices.
```
(r/slavelabour version uses `[OFFER]` and leans budget-friendly.)

## Saving

```
/gigs/listings/
  fiverr/[product].md
  craigslist/[product].md
  reddit/[product].md
  POST_CHECKLIST.md   ← where to post each, posting cadence, what stays manual
```

Generate `POST_CHECKLIST.md` listing each file, the exact platform/section/sub to post it to, and the allowed re-post cadence per platform.

## Cadence (so inbound doesn't become spam either)

- **Fiverr / Craigslist services:** post once; refresh per platform rules (CL services can be reposted every ~48h). Don't post the same ad to 20 CL cities at once — CL ghosts duplicate ads. A few relevant cities, staggered.
- **Reddit [FOR HIRE]:** most subs allow one post every 24-48h. Respect it or get banned.
- Quality and restraint protect inbound accounts the same way they protect outbound ones.

## Guardrails (do not cross)

- **Never script posting to Fiverr/Upwork/Reddit.** These platforms ban automation and scraping. This skill *generates* listings; the human posts them. That boundary is what keeps the accounts alive.
- No multiple accounts to dodge limits, no fake reviews, no inflated claims. One ban wave erases the whole operation.
- Inbound is the closest thing to passive — but a human still posts the listings, handles orders, sends work, and collects payment. There is no fully passive version that survives.

## After generating

```
## Inbound listings ready

Generated [N] listings across Fiverr / Craigslist services / Reddit.
→ /gigs/listings/  (see POST_CHECKLIST.md for where + how often to post)

Fastest first dollar: post the Fiverr gig + one Reddit [FOR HIRE] today,
price Basic low, deliver fast, ask for a review. Reviews are the unlock.
```
