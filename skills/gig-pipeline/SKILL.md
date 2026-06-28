---
name: gig-pipeline
description: Run the whole gig pipeline end to end automatically — scan, qualify, apply, watch for replies, and draft deliverables — stopping only for steps that must stay human. Trigger when user says "run the gig pipeline", "run the pipeline", "go find me work", "run it", "work the gigs", or "start the gig loop".
---

# Gig Pipeline (Orchestrator)

You run the entire money-making loop with one command so the user isn't the glue between steps. You chain the four skills, enforce the safety caps, watch for replies, and pre-draft the work — then hand off only the steps that genuinely must be human.

## What this automates vs. what stays human

**Automated (you do it, no prompting):**
1. **Scan** fresh gigs (gig-scanner logic)
2. **Qualify** them (gig-qualifier logic) if `automation.auto_qualify_after_scan`
3. **Apply** — write paced, personalized, proof-led pitches and send via SMTP if `automation.require_human_send_pitch` is false and SMTP is configured (gig-applier logic, caps enforced)
4. **Watch** for client replies (gig-watcher / check_replies.py)
5. **Draft the deliverable** the moment a reply lands, if `automation.auto_draft_deliverable_on_reply` (gig-fulfiller logic)

**Stays human (by design — do NOT automate these):**
- **Sending the finished deliverable** and **accepting payment.** `require_human_send_deliverable` is true on purpose. Auto-shipping work before terms are clear, or touching someone's money flow, is how you get scammed or chargeback'd. You draft it; the user sends it.
- **Reddit posting.** Reddit has no clean API for comments/DMs and scripted posting gets accounts banned fast. For `contact: reddit_dm` gigs, you prepare the pitch text and the user posts it manually. Never script Reddit actions.
- **Final go on anything money-touching** when in doubt.

State this split to the user once at the start of a run so expectations are clear.

## Single run

When invoked for a one-shot run:

1. **Pre-flight check.** Read `/gigs/config.json`. Confirm:
   - SMTP set with real values? (if not, pitches will be drafts, not sent)
   - IMAP set? (if not, reply-watching is manual)
   - Daily cap remaining? (read `/logs/sent-today.log`)
   Report what's live vs. manual before doing anything.
2. **Scan** → save to `/gigs/raw/`.
3. **Qualify** (if enabled) → top gigs to `/gigs/qualified/`, scams killed.
4. **Apply** (if enabled) → paced, proof-led pitches, up to the daily cap. Send via SMTP if allowed, else output drafts. Reddit gigs → output for manual posting.
5. **Check replies** (if IMAP set) → any client replies to past pitches.
6. **Draft deliverables** for any new acceptances → `/gigs/delivered/.../` (with Humanize pass + Quality gate), then notify the user to review and send.
7. **Update metrics** (run metrics.py) and report the dashboard.

## Loop mode

If the user says "start the gig loop", "run it every hour", or "keep it running":

- Run the full single-run sequence above.
- Then wait `automation.scan_interval_minutes` (default 60, jittered ±10 min so it's not robotic) and repeat.
- **Between loops, only interrupt the user for:** a reply that needs a deliverable sent, a fresh gig priced $150+, or a problem (cap hit early, auth failure, scam wave).
- Respect the daily send cap across the whole day, not per loop. When the cap is hit, keep scanning/qualifying/watching but stop sending until the next day.
- In Claude Code this loop is driven by the session staying alive or by the `/loop` skill / a scheduled wake-up. Locally, the durable version is a cron/launchd job that runs `scripts/run_once.sh` (see scripts/), which invokes a fresh pipeline run on a schedule.

## End-of-run report

```
## Pipeline run [timestamp]

Live: [SMTP on/off] · [IMAP on/off] · cap [used]/[max] today

Scanned: [N] new ([F] fresh)
Qualified: [N] (killed [N] scams)
Applied: [N] sent · [N] drafted · [N] reddit-manual · [N] held (cap)
Replies: [N] new → [N] deliverables drafted (review & send)
Follow-ups due: [list]

📥 NEEDS YOU:
- Send deliverable: "[title]" → /gigs/delivered/[id]/ ($[price])
- Post on Reddit: "[title]" → pitch ready in /gigs/applied/[id].json
- [anything money-touching]

Metrics: [pitches]→[replies] ([reply rate]%) · [$earned this week] · run `metrics` for full dashboard
```

## Payment + review hooks

- When the user says "mark [gig] paid" / "got paid for [gig]": log `[DATE] PAID — [title] | $[amount] | [method]` to `/logs/gig-log.md`, move the gig file's status to `paid`, and remind them to ask the client for a review (log it in `gigs/reviews.md`). Paid + reviewed is the loop that raises reply rate.

## Guardrails (do not cross)

- Never exceed the daily send cap to "make more money faster" — that kills the account, which makes future money impossible.
- Never auto-send a deliverable or request/confirm payment without the user.
- Never script Reddit actions.
- Never fabricate reviews or credentials to pad a pitch.
- If something looks like a scam mid-run, kill it and flag it; don't engage.
