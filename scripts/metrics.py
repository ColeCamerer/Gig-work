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
from collections import defaultdict
from datetime import datetime, date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "logs", "gig-log.md")
OUT = os.path.join(ROOT, "gigs", "metrics.md")

ACTIONS = ("APPLIED", "REPLIED", "DELIVERED", "PAID", "REJECTED")
LINE = re.compile(r'^(\d{4}-\d{2}-\d{2}).*?\b(APPLIED|REPLIED|DELIVERED|PAID|REJECTED)\b(.*)$')
MONEY = re.compile(r'\$(\d+)')


def iso_week(d):
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


def main():
    if not os.path.exists(LOG):
        print("No log yet at logs/gig-log.md — run the pipeline first.")
        return

    weeks = defaultdict(lambda: {a: 0 for a in ACTIONS} | {"paid_amount": 0})
    totals = {a: 0 for a in ACTIONS}
    total_paid = 0

    with open(LOG) as f:
        for raw in f:
            m = LINE.match(raw.strip())
            if not m:
                continue
            day, action, rest = m.group(1), m.group(2), m.group(3)
            try:
                d = datetime.strptime(day, "%Y-%m-%d").date()
            except ValueError:
                continue
            wk = iso_week(d)
            weeks[wk][action] += 1
            totals[action] += 1
            if action == "PAID":
                mm = MONEY.search(rest)
                if mm:
                    amt = int(mm.group(1))
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
