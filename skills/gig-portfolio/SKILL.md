---
name: gig-portfolio
description: Generate polished proof samples for each service lane so pitches and listings have real work to show from day one. Trigger when user says "build my portfolio", "make samples", "generate proof", "seed samples", or at first setup before any client work exists.
---

# Gig Portfolio

Every lane converts on proof, and a brand-new operator has none. This skill manufactures that proof: 1-2 polished sample deliverables per lane, saved to `gigs/samples/`, ready to drop into pitches ("here's a quick taste"), Fiverr gig galleries, and Reddit replies. It removes the cold-start handicap before the first client exists.

## What to generate

Read `gigs/catalog.json`. For each lane the user wants to offer (default: the high-demand text lanes + logo), produce a realistic, genuinely good sample on an invented-but-plausible client scenario:

- **Text lanes** → full sample deliverable (a real blog post, a real 5-pack of product descriptions, a real resume rewrite using fictional but realistic history, a real ad set, etc.)
- **Design lanes** → if `OPENAI_API_KEY` is set, generate the image; otherwise produce the design brief + spec + the exact generation prompt so it's one paste from a finished sample.

Make samples diverse (different industries/tones) so they prove range. Quality bar = the fulfiller's Humanize pass + Quality gate. A weak sample is worse than none.

## Rules

- Mark every sample clearly as a sample, on a fictional client, e.g. `[Sample — fictional client, demonstrates style]`. Never imply it was paid client work or invent a real client's name.
- Run the same Humanize pass as the fulfiller — samples must read human, or they advertise the opposite of what you're selling.
- One strong sample per lane beats five mediocre ones.

## Output

```
gigs/samples/
  blog-[topic].md
  product-copy-[niche].md
  resume-[role].md
  ad-copy-[product].md
  email-[type].md
  logo-[industry]-spec.md   (+ .png if key set)
  INDEX.md   ← one-line description + which lane each sample proves
```

Generate `INDEX.md` mapping each sample to its lane and a one-line "use this when pitching X" note, so the applier/closer can grab the right proof instantly.

## After generating

```
## Portfolio seeded
Generated [N] samples across [lanes].
→ gigs/samples/ (see INDEX.md)

Use these as the free "here's a taste" in pitches and as Fiverr gallery items.
Swap each one out for real paid work as it comes in — real client samples
(with permission) convert better than manufactured ones.
```

## Upgrade path

As real jobs complete, the fulfiller saves standout deliverables to `gigs/samples/` too. Over time the manufactured samples get replaced by real ones — better proof, and the portfolio compounds with the business.
