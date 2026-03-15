#!/usr/bin/env python3
"""Vérifie la boîte de réception via IMAP. Sécurisé avec contexte SSL.

Usage:
    python3 check-inbox.py unread         # emails non lus
    python3 check-inbox.py all 10         # les 10 derniers

Les credentials sont lus depuis les variables d'environnement :
    AGENT_IMAP_HOST, AGENT_IMAP_USER, AGENT_IMAP_PASS, AGENT_IMAP_PORT (défaut: 993)
"""
import imaplib
import email
import ssl
import os
import sys
import json
from email.header import decode_header


def check_inbox(mode: str = "unread", limit: int = 10):
    host = os.environ.get("AGENT_IMAP_HOST")
    user = os.environ.get("AGENT_IMAP_USER")
    password = os.environ.get("AGENT_IMAP_PASS")
    port = int(os.environ.get("AGENT_IMAP_PORT", "993"))

    if not all([host, user, password]):
        print("Erreur : variables AGENT_IMAP_HOST, AGENT_IMAP_USER, AGENT_IMAP_PASS requises")
        sys.exit(1)

    context = ssl.create_default_context()
    mail = imaplib.IMAP4_SSL(host, port, ssl_context=context)
    mail.login(user, password)
    mail.select("INBOX")

    if mode == "unread":
        _, data = mail.search(None, "UNSEEN")
    else:
        _, data = mail.search(None, "ALL")

    ids = data[0].split()[-limit:] if data[0] else []
    results = []

    for mid in ids:
        _, msg_data = mail.fetch(mid, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])

        subject = decode_header(msg["Subject"] or "")[0][0]
        if isinstance(subject, bytes):
            subject = subject.decode(errors="replace")

        sender = msg["From"] or ""
        date = msg["Date"] or ""

        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = payload.decode(errors="replace")
                    break
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode(errors="replace")

        results.append({
            "from": sender,
            "subject": str(subject),
            "date": date,
            "body": body[:500],
        })

    mail.logout()
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "unread"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    check_inbox(mode, limit)
