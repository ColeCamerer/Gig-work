# Flaw Audit & Solutions

Operator's honest audit of weaknesses in the system, the options considered for
each, and the chosen fix. Ordered by severity.

---

## 1. CRITICAL — Secrets leak to GitHub

**Flaw:** `gigs/config.json` is git-tracked and the workflow auto-commits/pushes.
The moment you put a real Gmail app password (SMTP/IMAP) in it, the credential is
pushed to the remote repo — permanently in history, even if deleted later.

**Options:**
| Option | Pros | Cons |
|---|---|---|
| A. Move all config to env vars | Most standard, nothing secret on disk | High setup friction; loses versioned non-secret settings |
| B. `.gitignore` the whole config.json | Simple | Loses version control of non-secret settings; easy to lose your tuning |
| C. Split: `config.json` (non-secret, tracked) + `secrets.json` (gitignored) + env override | Versioned settings AND secrets stay local; low friction | One extra file |

**Chosen: C.** Best balance — your tuning stays in git, secrets never leave your
machine, and env vars can override in CI. A loader merges them.

---

## 2. HIGH — Daily send-cap can get stuck "full" forever

**Flaw:** the cap relied on `logs/sent-today.log` being truncated by `run_once.sh`.
If you run the pipeline via Claude Code or `/loop` (not the shell script), the file
never resets, so after one full day the system thinks the cap is permanently hit and
stops sending.

**Options:**
| Option | Pros | Cons |
|---|---|---|
| A. Truncate file daily via cron only | Already written | Breaks for any non-cron run (the common case) |
| B. Timestamp every send; count only *today's* rows | Reset-free, correct under any runner | Tiny parse step |

**Chosen: B.** Make the cap date-aware: `gigs/sent-log.csv` with a timestamp per
send; "remaining" = max − count(rows where date == today). No reset needed, correct
no matter how it's launched.

---

## 3. HIGH — The learning loop is blind to inbound channels

**Flaw:** `learn.py`/`metrics.py` only see outbound email gigs (JSON files +
IMAP-detected replies). Fiverr orders and Reddit DMs — the main inbound money — leave
no record, so the "learn what converts" engine optimizes on half the data and could
tell you to drop a lane that's actually winning on Fiverr.

**Options:**
| Option | Pros | Cons |
|---|---|---|
| A. Keep per-gig JSON only | No change | Permanently blind to inbound |
| B. One ledger (`gigs/ledger.csv`) + a `gig.py` CLI to record any job through stages (pitched→replied→delivered→paid) across all channels | Single source of truth; phone-friendly one-liners; metrics/learn get full vision | Requires logging each event (CLI makes it trivial) |

**Chosen: B.** A unified ledger is the spine the whole feedback loop needs.
`metrics.py` and `learn.py` read it, so Fiverr/Reddit/Craigslist all count and the
operator's reallocation decisions are based on complete data.

---

## 4. MEDIUM — Quality gate is graded by the same pass that wrote the work

**Flaw:** the fulfiller's quality check is self-assessment by the model that just
wrote the piece — blind spots survive, and a weak deliverable on a young account
risks the refund/bad-review death spiral.

**Options:**
| Option | Pros | Cons |
|---|---|---|
| A. Trust single-pass self-check | Free | Misses its own blind spots |
| B. Separate red-team critique pass (fresh critical lens, optionally a 2nd model) before saving | Catches what the writer missed; cheap | One extra step |
| C. External AI-detector API gate | "Objective" | Unreliable, dishonest to rely on, adds dependency |

**Chosen: B.** Add an explicit red-team review step to the fulfiller — re-read as a
skeptical client looking for reasons not to pay, fix what's found, then save.

---

## 5. ACKNOWLEDGED LIMITS (no clean code fix — handled by honesty/process)

- **Inbound replies (Fiverr/Reddit) can't be auto-detected** like email — those
  platforms ban scraping/automation. Mitigation: notification cadence + you paste the
  reply to the closer. Documented, not pretended away.
- **Non-payment on direct deals** (Craigslist/Reddit have no escrow). Mitigation in
  the closer: 50% up front over ~$75, watermarked/preview-first on bigger jobs.
- **Single-account fragility.** Mitigation is the entire anti-flag design; the real
  protection is not abusing the caps. No multi-account workaround — that's a ban vector.
- **Human throughput ceiling** (you send/collect). Real but not a day-one problem.

These are inherent to doing this legitimately. The fix is process and honesty, not
code that pretends the limit away.
