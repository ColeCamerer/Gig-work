"""
_config.py — shared config loader + runtime helpers for all gig scripts.

Fixes two audited flaws:
- Secrets never live in the tracked config.json. Real creds go in gigs/secrets.json
  (gitignored) or env vars, merged over config.json here.
- The daily send cap is date-aware (counts today's rows in sent-log.csv), so it
  resets correctly no matter how the pipeline is launched.

stdlib only.
"""
import os
import json
import csv
from datetime import datetime, timezone, date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(ROOT, "gigs", "config.json")
SECRETS = os.path.join(ROOT, "gigs", "secrets.json")
SENT_LOG = os.path.join(ROOT, "gigs", "sent-log.csv")
LEDGER = os.path.join(ROOT, "gigs", "ledger.csv")

ENV_MAP = {
    ("smtp", "username"): "GIG_SMTP_USERNAME",
    ("smtp", "password"): "GIG_SMTP_PASSWORD",
    ("imap", "username"): "GIG_IMAP_USERNAME",
    ("imap", "password"): "GIG_IMAP_PASSWORD",
}


def _deep_merge(base, over):
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v
    return base


def load_config():
    """config.json <- secrets.json <- env vars (later wins)."""
    cfg = {}
    if os.path.exists(CONFIG):
        with open(CONFIG) as f:
            cfg = json.load(f)
    if os.path.exists(SECRETS):
        try:
            with open(SECRETS) as f:
                _deep_merge(cfg, json.load(f))
        except Exception:
            pass
    for (block, key), env in ENV_MAP.items():
        val = os.environ.get(env)
        if val:
            cfg.setdefault(block, {})[key] = val
    return cfg


def is_live(val):
    """True if a config value looks like a real (non-placeholder) value."""
    if not val:
        return False
    s = str(val).lower()
    return not (s.startswith("your") or s.startswith("you@") or s in ("", "_about"))


def smtp_ready(cfg):
    s = cfg.get("smtp", {})
    return is_live(s.get("username")) and is_live(s.get("password"))


def imap_ready(cfg):
    s = cfg.get("imap", {})
    return is_live(s.get("username")) and is_live(s.get("password"))


# ---- date-aware send cap ----

def _today():
    return date.today().isoformat()


def sent_today():
    """Count sends logged today (date-aware; no reset needed)."""
    if not os.path.exists(SENT_LOG):
        return 0
    n = 0
    today = _today()
    with open(SENT_LOG, newline="") as f:
        for row in csv.reader(f):
            if row and row[0].startswith(today):
                n += 1
    return n


def remaining_cap(cfg):
    cap = cfg.get("sending", {}).get("max_applications_per_day", 8)
    return max(0, cap - sent_today())


def record_sent(channel, dest):
    """Append a timestamped send so the cap can count today's correctly."""
    new = not os.path.exists(SENT_LOG)
    with open(SENT_LOG, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["timestamp", "channel", "dest"])
        w.writerow([datetime.now(timezone.utc).isoformat(), channel, dest])


# ---- unified job ledger (all channels) ----

LEDGER_HEADER = ["timestamp", "stage", "channel", "lane", "title", "price"]
STAGES = ["pitched", "replied", "delivered", "paid", "lost"]


def ledger_rows():
    if not os.path.exists(LEDGER):
        return []
    out = []
    with open(LEDGER, newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            out.append(row)
    return out


def record_ledger(stage, channel, lane, title, price):
    new = not os.path.exists(LEDGER)
    with open(LEDGER, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(LEDGER_HEADER)
        w.writerow([datetime.now(timezone.utc).isoformat(), stage, channel, lane, title, price])
