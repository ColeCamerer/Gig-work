#!/usr/bin/env python3
"""
learn.py — the feedback loop. Mine real results to find what actually converts,
then recommend where to concentrate effort.

Reads every gig record (gigs/applied/*.json and gigs/delivered/*/gig.json),
buckets by subtype, platform, and price band, and computes the only metric
that matters for allocation: dollars earned per pitch sent. Writes
gigs/insights.md with ranked winners/losers and concrete next-move advice.

This is what turns a static pipeline into a compounding business: each cycle
it tells the operator to do more of what pays and stop what doesn't.
stdlib only.  Usage: python3 scripts/learn.py
"""
import os
import sys
import json
import glob
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _config as C  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPLIED = os.path.join(ROOT, "gigs", "applied")
DELIVERED = os.path.join(ROOT, "gigs", "delivered")
OUT = os.path.join(ROOT, "gigs", "insights.md")

REPLIED_STATES = {"replied", "delivered", "paid"}
PAID_STATES = {"paid"}


def load_records():
    recs = []
    for p in glob.glob(os.path.join(APPLIED, "*.json")):
        try:
            recs.append(json.load(open(p)))
        except Exception:
            pass
    for p in glob.glob(os.path.join(DELIVERED, "*", "gig.json")):
        try:
            recs.append(json.load(open(p)))
        except Exception:
            pass
    # Fold in the unified ledger (Fiverr/Reddit/Craigslist inbound + outbound).
    # Collapse each (channel,lane,title) to its most-advanced stage.
    led = {}
    stage_status = {"pitched": "applied", "replied": "replied",
                    "delivered": "delivered", "paid": "paid", "lost": "applied"}
    for row in C.ledger_rows():
        key = (row.get("channel"), row.get("lane"), row.get("title"))
        status = stage_status.get(row.get("stage"), "applied")
        try:
            price = int(row.get("price") or 0)
        except ValueError:
            price = 0
        rec = {"id": "ledger:" + "|".join(str(k) for k in key),
               "subtype": row.get("lane"), "type": row.get("lane"),
               "price": price, "status": status,
               "city": "reddit" if row.get("channel") == "reddit" else row.get("channel"),
               "category": row.get("channel")}
        if key not in led or _rank(rec) > _rank(led[key]):
            led[key] = rec
    recs.extend(led.values())

    # de-dupe by id (a gig may exist in both applied and delivered)
    by_id = {}
    for r in recs:
        rid = r.get("id")
        # prefer the most-advanced status
        if rid not in by_id or _rank(r) > _rank(by_id[rid]):
            by_id[rid] = r
    return list(by_id.values())


def _rank(r):
    order = {"applied": 1, "replied": 2, "delivered": 3, "paid": 4}
    return order.get(r.get("status"), 0)


def price_band(p):
    p = p or 0
    if p == 0:
        return "unstated"
    if p < 50:
        return "$30-49"
    if p < 100:
        return "$50-99"
    return "$100+"


def platform_of(r):
    cat = r.get("category")
    if r.get("city") == "reddit" or r.get("contact") == "reddit_dm":
        return "reddit/" + (cat or "?")
    if cat and cat not in ("wrg", "crg", "cpg"):
        return cat  # fiverr, upwork, etc. from the ledger
    return "craigslist"


def got_reply(r):
    return r.get("status") in REPLIED_STATES or bool(r.get("reply"))


def got_paid(r):
    return r.get("status") in PAID_STATES


def bucketize(recs, keyfn):
    b = defaultdict(lambda: {"n": 0, "replies": 0, "paid": 0, "earned": 0})
    for r in recs:
        k = keyfn(r)
        b[k]["n"] += 1
        if got_reply(r):
            b[k]["replies"] += 1
        if got_paid(r):
            b[k]["paid"] += 1
            b[k]["earned"] += r.get("price", 0) or 0
    return b


def fmt_table(title, b):
    if not b:
        return [f"### {title}\n_No data yet._\n"]
    rows = sorted(b.items(), key=lambda kv: (kv[1]["earned"] / kv[1]["n"] if kv[1]["n"] else 0), reverse=True)
    out = [f"### {title}", "", "| Bucket | Pitches | Replies | Reply% | Paid | $ Earned | $/pitch |",
           "|---|---|---|---|---|---|---|"]
    for k, v in rows:
        rr = f"{100*v['replies']/v['n']:.0f}%" if v["n"] else "—"
        pp = f"${v['earned']/v['n']:.0f}" if v["n"] else "—"
        out.append(f"| {k} | {v['n']} | {v['replies']} | {rr} | {v['paid']} | ${v['earned']} | {pp} |")
    out.append("")
    return out


def recommendations(recs, by_sub, by_plat, by_price):
    lines = ["## Next moves", ""]
    total = len(recs)
    paid = sum(1 for r in recs if got_paid(r))
    if total < 10:
        lines.append(f"- **Not enough data yet ({total} pitches).** Keep running — learn.py gets sharp around 20-30 pitches. Until then, trust the defaults and lead every pitch with proof.")
        return lines

    # best subtype by $/pitch with at least 3 pitches
    def best(b, label):
        cand = [(k, v) for k, v in b.items() if v["n"] >= 3]
        if not cand:
            return None
        k, v = max(cand, key=lambda kv: kv[1]["earned"] / kv[1]["n"])
        return k, v

    bs = best(by_sub, "subtype")
    if bs:
        k, v = bs
        lines.append(f"- **Concentrate on {k}** — your best earner at ${v['earned']/v['n']:.0f}/pitch ({v['paid']} paid of {v['n']}). Bias the qualifier toward it and build a Fiverr/inbound listing for it.")
    bp = best(by_plat, "platform")
    if bp:
        k, v = bp
        lines.append(f"- **Best platform: {k}** (${v['earned']/v['n']:.0f}/pitch). Shift more daily-cap budget here.")
    bpr = best(by_price, "price band")
    if bpr:
        k, v = bpr
        lines.append(f"- **Sweet-spot price band: {k}.** Target gigs here and price inbound listings to match.")

    # dead weight
    dead = [k for k, v in by_sub.items() if v["n"] >= 5 and v["replies"] == 0]
    if dead:
        lines.append(f"- **Stop spending pitches on: {', '.join(dead)}** — 0 replies across 5+ tries. Drop from targeting.")

    if paid == 0:
        lines.append("- **Still no paid jobs.** Reply rate, not volume, is the problem. Strengthen the proof sample, apply faster after posting, and lower first-listing prices to buy a review.")
    return lines


def main():
    recs = load_records()
    by_sub = bucketize(recs, lambda r: r.get("subtype") or r.get("type") or "?")
    by_plat = bucketize(recs, platform_of)
    by_price = bucketize(recs, lambda r: price_band(r.get("price")))

    out = ["# Conversion Insights", "",
           "_What actually converts — do more of the top rows, kill the bottom._", ""]
    out += fmt_table("By job type", by_sub)
    out += fmt_table("By platform", by_plat)
    out += fmt_table("By price band", by_price)
    out += recommendations(recs, by_sub, by_plat, by_price)

    text = "\n".join(out) + "\n"
    with open(OUT, "w") as f:
        f.write(text)
    print(text)


if __name__ == "__main__":
    main()
