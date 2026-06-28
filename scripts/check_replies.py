#!/usr/bin/env python3
"""
check_replies.py — detect client replies to gig pitches via Gmail IMAP.

Reads /gigs/applied/*.json, collects the addresses you pitched, then scans the
inbox for messages FROM those addresses. Any match is a client reply: the gig
file is marked "replied", the message is saved, and a JSON summary is printed
so the orchestrator can route it to the fulfiller to draft a deliverable.

Read-only on the mailbox (uses BODY.PEEK, never marks mail seen). stdlib only.

Usage:  python3 scripts/check_replies.py
Exit 0 always; prints JSON {"replies": [...], "errors": [...]} to stdout.
"""
import imaplib
import email
import json
import os
import re
import sys
from email.header import decode_header
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPLIED = os.path.join(ROOT, "gigs", "applied")
CONFIG = os.path.join(ROOT, "gigs", "config.json")


def load_config():
    with open(CONFIG) as f:
        return json.load(f)


def norm_addr(s):
    m = re.search(r'[\w\.\-\+]+@[\w\.\-]+\.\w+', s or "")
    return m.group(0).lower() if m else ""


def decode_str(s):
    if not s:
        return ""
    parts = decode_header(s)
    out = []
    for text, enc in parts:
        if isinstance(text, bytes):
            out.append(text.decode(enc or "utf-8", errors="ignore"))
        else:
            out.append(text)
    return "".join(out)


def get_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and "attachment" not in str(part.get("Content-Disposition")):
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode(part.get_content_charset() or "utf-8", errors="ignore")
        return ""
    payload = msg.get_payload(decode=True)
    return payload.decode(msg.get_content_charset() or "utf-8", errors="ignore") if payload else ""


def applied_index():
    """Map pitched-address -> gig file path, for email gigs only."""
    idx = {}
    if not os.path.isdir(APPLIED):
        return idx
    for fn in os.listdir(APPLIED):
        if not fn.endswith(".json"):
            continue
        path = os.path.join(APPLIED, fn)
        try:
            g = json.load(open(path))
        except Exception:
            continue
        if g.get("status") not in ("applied",):
            continue
        addr = norm_addr(g.get("sent_to", ""))
        if addr and "@" in addr:
            idx[addr] = path
    return idx


def main():
    errors, replies = [], []
    try:
        cfg = load_config()
    except Exception as e:
        print(json.dumps({"replies": [], "errors": [f"config: {e}"]}))
        return

    imap = cfg.get("imap", {})
    if not imap or imap.get("username", "").startswith("your@") or not imap.get("password") or imap.get("password", "").startswith("your-"):
        print(json.dumps({"replies": [], "errors": ["IMAP not configured — set gigs/config.json imap block. Reply-watching is manual until then."]}))
        return

    idx = applied_index()
    if not idx:
        print(json.dumps({"replies": [], "errors": ["No email gigs in /gigs/applied/ to watch."]}))
        return

    try:
        M = imaplib.IMAP4_SSL(imap["host"], imap.get("port", 993))
        M.login(imap["username"], imap["password"])
        M.select("INBOX")
    except Exception as e:
        print(json.dumps({"replies": [], "errors": [f"IMAP login: {e}"]}))
        return

    for addr, path in idx.items():
        try:
            # search unseen messages from this address (don't mark seen)
            typ, data = M.search(None, '(FROM "%s")' % addr)
            if typ != "OK":
                continue
            ids = data[0].split()
            if not ids:
                continue
            latest = ids[-1]
            typ, msg_data = M.fetch(latest, "(BODY.PEEK[])")
            if typ != "OK":
                continue
            msg = email.message_from_bytes(msg_data[0][1])
            subject = decode_str(msg.get("Subject"))
            body = get_body(msg).strip()
            date = msg.get("Date", "")

            g = json.load(open(path))
            g["status"] = "replied"
            g["reply"] = {
                "from": addr,
                "subject": subject,
                "body": body[:4000],
                "received": date,
                "detected_at": datetime.now(timezone.utc).isoformat(),
            }
            with open(path, "w") as f:
                json.dump(g, f, indent=2)

            replies.append({
                "gig_id": g.get("id"),
                "title": g.get("title"),
                "price": g.get("price"),
                "subtype": g.get("subtype"),
                "from": addr,
                "subject": subject,
                "body": body[:4000],
                "gig_file": path,
            })
        except Exception as e:
            errors.append(f"{addr}: {e}")

    try:
        M.logout()
    except Exception:
        pass

    print(json.dumps({"replies": replies, "errors": errors}, indent=2))


if __name__ == "__main__":
    main()
