#!/usr/bin/env python3
"""Envoie un email via SMTP. Sécurisé - pas d'interpolation shell.

Usage:
    python3 send-email.py "dest@mail.fr" "Sujet" "Corps du message" ["cc@optionnel.fr"]

Les credentials sont lus depuis les variables d'environnement :
    AGENT_SMTP_HOST, AGENT_SMTP_USER, AGENT_SMTP_PASS, AGENT_SMTP_PORT (défaut: 587)
"""
import html
import smtplib
import ssl
import sys
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path


def load_signature():
    """Charge la signature HTML si elle existe."""
    sig_path = Path(__file__).parent.parent / "signature.html"
    if sig_path.exists():
        return sig_path.read_text(encoding="utf-8")
    return ""


def send_email(to: str, subject: str, body: str, cc: str = ""):
    host = os.environ.get("AGENT_SMTP_HOST")
    user = os.environ.get("AGENT_SMTP_USER")
    password = os.environ.get("AGENT_SMTP_PASS")
    port = int(os.environ.get("AGENT_SMTP_PORT", "587"))

    if not all([host, user, password]):
        print("Erreur : variables AGENT_SMTP_HOST, AGENT_SMTP_USER, AGENT_SMTP_PASS requises")
        sys.exit(1)

    msg = MIMEMultipart("alternative")
    msg["From"] = user
    msg["To"] = to
    msg["Subject"] = subject
    if cc:
        msg["Cc"] = cc

    signature = load_signature()
    body_html = (
        "<html><body><p>"
        + html.escape(body).replace("\n", "<br>")
        + "</p><br>"
        + signature
        + "</body></html>"
    )
    msg.attach(MIMEText(body, "plain", "utf-8"))
    msg.attach(MIMEText(body_html, "html", "utf-8"))

    context = ssl.create_default_context()
    recipients = [to]
    if cc:
        recipients.append(cc)

    try:
        with smtplib.SMTP(host, port) as server:
            server.starttls(context=context)
            server.login(user, password)
            server.sendmail(user, recipients, msg.as_string())
        print(f"Email envoyé à {to}" + (f" (CC: {cc})" if cc else ""))
    except Exception as e:
        print(f"Erreur d'envoi : {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 send-email.py <to> <subject> <body> [cc]")
        sys.exit(1)
    send_email(
        to=sys.argv[1],
        subject=sys.argv[2],
        body=sys.argv[3],
        cc=sys.argv[4] if len(sys.argv) > 4 else "",
    )
