#!/usr/bin/env python3
"""
gig.py — record any job event across any channel in one ledger.

Fixes the "learning loop is blind to inbound" flaw: Fiverr orders, Reddit DMs,
and Craigslist deals all log to gigs/ledger.csv with one command, so metrics.py
and learn.py see the whole business — not just outbound email.

Usage:
  gig.py log <stage> --channel fiverr --lane RESUME_LINKEDIN --title "resume rewrite" --price 60
  gig.py status                 # quick funnel + cap snapshot
  gig.py cap                    # how many sends left today

Stages: pitched | replied | delivered | paid | lost
Log each stage as it happens (it's fine to log only the stages you reach).
"""
import sys
import os
import argparse
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _config as C  # noqa: E402


def cmd_log(a):
    if a.stage not in C.STAGES:
        print(f"stage must be one of: {', '.join(C.STAGES)}")
        return 1
    C.record_ledger(a.stage, a.channel, a.lane, a.title, a.price)
    if a.stage == "paid":
        print(f"logged PAID: {a.title} ${a.price} ({a.channel}/{a.lane}) — now ask for a review!")
    else:
        print(f"logged {a.stage}: {a.title} ({a.channel}/{a.lane})")
    return 0


def cmd_status(a):
    rows = C.ledger_rows()
    by_stage = Counter(r["stage"] for r in rows)
    earned = sum(int(r["price"] or 0) for r in rows if r["stage"] == "paid")
    cfg = C.load_config()
    print("Funnel (all channels):")
    for s in C.STAGES:
        print(f"  {s:10} {by_stage.get(s, 0)}")
    print(f"Earned total: ${earned}")
    print(f"Sends today: {C.sent_today()} / cap {cfg.get('sending',{}).get('max_applications_per_day',8)} "
          f"(remaining {C.remaining_cap(cfg)})")
    return 0


def cmd_cap(a):
    cfg = C.load_config()
    print(C.remaining_cap(cfg))
    return 0


def main():
    p = argparse.ArgumentParser(prog="gig.py")
    sub = p.add_subparsers(dest="cmd", required=True)

    pl = sub.add_parser("log", help="record a job stage")
    pl.add_argument("stage")
    pl.add_argument("--channel", default="?", help="fiverr|reddit|craigslist|upwork|...")
    pl.add_argument("--lane", default="?", help="catalog lane, e.g. RESUME_LINKEDIN")
    pl.add_argument("--title", default="")
    pl.add_argument("--price", default="0")
    pl.set_defaults(fn=cmd_log)

    ps = sub.add_parser("status", help="funnel + cap snapshot")
    ps.set_defaults(fn=cmd_status)

    pc = sub.add_parser("cap", help="sends remaining today")
    pc.set_defaults(fn=cmd_cap)

    a = p.parse_args()
    sys.exit(a.fn(a))


if __name__ == "__main__":
    main()
