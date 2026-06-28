#!/usr/bin/env python3
"""
metrics.py — turn the activity log into a weekly performance dashboard.

Parses /logs/gig-log.md for APPLIED / REPLIED / DELIVERED / PAID / REJECTED
lines, groups by ISO week, and computes reply rate, close rate, and money
earned. Writes /gigs/metrics.md and prints the same to stdout.

Reply rate is the number to watch: it should climb as you collect reviews.
stdlib only.  Usage: python3 scripts/metrics.py
"""
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _config as C  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "logs", "gig-log.md")
OUT = os.path.join(ROOT, "gigs", "metrics.md")

ACTIONS = ("APPLIED", "REPLIED", "DELIVERED", "PAID", "REJECTED")
LINE = re.compile(r'^(\d{4}-\d{2}-\d{2}).*?\b(APPLIED|REPLIED|DELIVERED|PAID|REJECTED)\b(.*)$')
MONEY = re.compile(r'\$(\d+)')

# ledger stage -> metrics action
STAGE_ACTION = {"pitched": "APPLIED", "replied": "REPLIED", "delivered": "DELIVERED",
                "paid": "PAID", "lost": "REJECTED"}


def events_from_ledger():
    """Yield (date, action, amount) from the unified ledger (all channels)."""
    evs = []
    for row in C.ledger_rows():
        ts = row.get("timestamp", "")
        try:
            d = datetime.fromisoformat(ts.replace("Z", "+00:00")).date()
        except Exception:
            continue
        action = STAGE_ACTION.get(row.get("stage", ""))
        if not action:
            continue
        amt = 0
        if action == "PAID":
            try:
                amt = int(row.get("price") or 0)
            except ValueError:
                amt = 0
        evs.append((d, action, amt))
    return evs


def events_from_log():
    evs = []
    if not os.path.exists(LOG):
        return evs
    with open(LOG) as f:
        for raw in f:
            m = LINE.match(raw.strip())
            if not m:
                continue
            try:
                d = datetime.strptime(m.group(1), "%Y-%m-%d").date()
            except ValueError:
                continue
            amt = 0
            if m.group(2) == "PAID":
                mm = MONEY.search(m.group(3))
                amt = int(mm.group(1)) if mm else 0
            evs.append((d, m.group(2), amt))
    return evs


def iso_week(d):
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


def main():
    # Prefer the unified ledger (covers all channels); fall back to the log.
    events = events_from_ledger() or events_from_log()
    if not events:
        print("No data yet — log jobs with scripts/gig.py or run the pipeline first.")
        return

    weeks = defaultdict(lambda: {a: 0 for a in ACTIONS} | {"paid_amount": 0})
    totals = {a: 0 for a in ACTIONS}
    total_paid = 0

    for d, action, amt in events:
        wk = iso_week(d)
        weeks[wk][action] += 1
        totals[action] += 1
        if action == "PAID":
            weeks[wk]["paid_amount"] += amt
            total_paid += amt

    def rate(n, d):
        return f"{(100.0 * n / d):.0f}%" if d else "—"

    lines = []
    lines.append("# Gig Metrics\n")
    lines.append(f"_Generated {date.today().isoformat()}_\n")
    lines.append("**Reply rate is the number to watch — it climbs with reviews.**\n")
    lines.append("| Week | Applied | Replies | Reply % | Delivered | Paid | Close % | $ Earned |")
    lines.append("|------|---------|---------|---------|-----------|------|---------|----------|")
    for wk in sorted(weeks):
        w = weeks[wk]
        lines.append(
            f"| {wk} | {w['APPLIED']} | {w['REPLIED']} | {rate(w['REPLIED'], w['APPLIED'])} "
            f"| {w['DELIVERED']} | {w['PAID']} | {rate(w['PAID'], w['REPLIED'])} | ${w['paid_amount']} |"
        )

    lines.append("")
    lines.append("## All-time")
    lines.append(f"- Pitches sent: **{totals['APPLIED']}**")
    lines.append(f"- Replies: **{totals['REPLIED']}**  (reply rate {rate(totals['REPLIED'], totals['APPLIED'])})")
    lines.append(f"- Delivered: **{totals['DELIVERED']}**")
    lines.append(f"- Paid jobs: **{totals['PAID']}**  (close rate {rate(totals['PAID'], totals['REPLIED'])})")
    lines.append(f"- Rejected/screened out: **{totals['REJECTED']}**")
    lines.append(f"- **Total earned: ${total_paid}**")
    if totals["PAID"]:
        lines.append(f"- Avg per paid job: ${total_paid // totals['PAID']}")
    lines.append("")
    lines.append("> Targets: reply rate 1-4% early → 10-20% after 3-5 reviews. "
                 "If reply rate is stuck near 0 after ~30 pitches, the pitches or timing need work, not more volume.")

    text = "\n".join(lines) + "\n"
    with open(OUT, "w") as f:
        f.write(text)
    print(text)


if __name__ == "__main__":
    main()
