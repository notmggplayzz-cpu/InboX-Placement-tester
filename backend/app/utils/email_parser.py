import base64
import email
from datetime import datetime
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def parse_gmail_message(message: dict) -> dict:
    """Parse a Gmail API message into usable format."""
    msg_id = message.get("id")
    headers = message.get("payload", {}).get("headers", [])

    header_dict = {}
    for header in headers:
        header_dict[header.get("name", "").lower()] = header.get("value", "")

    return {
        "id": msg_id,
        "subject": header_dict.get("subject", ""),
        "from": header_dict.get("from", ""),
        "to": header_dict.get("to", ""),
        "date": header_dict.get("date", ""),
        "message_id": header_dict.get("message-id", ""),
        "thread_id": message.get("threadId"),
        "labels": message.get("labelIds", []),
        "snippet": message.get("snippet", ""),
    }


def get_message_body(message: dict) -> tuple[Optional[str], Optional[str]]:
    """Extract HTML and plain text body from Gmail message."""
    html_body = None
    text_body = None

    payload = message.get("payload", {})

    if "parts" in payload:
        for part in payload["parts"]:
            mime_type = part.get("mimeType", "")
            if mime_type == "text/html":
                data = part.get("body", {}).get("data", "")
                if data:
                    html_body = base64.urlsafe_b64decode(data).decode("utf-8")
            elif mime_type == "text/plain":
                data = part.get("body", {}).get("data", "")
                if data:
                    text_body = base64.urlsafe_b64decode(data).decode("utf-8")
    else:
        data = payload.get("body", {}).get("data", "")
        if data:
            text_body = base64.urlsafe_b64decode(data).decode("utf-8")

    return html_body, text_body


def create_mime_message(
    sender: str,
    to: str,
    subject: str,
    html_body: str,
    text_body: Optional[str] = None,
    headers: Optional[dict] = None,
) -> str:
    """Create a MIME message and return base64 encoded string."""
    message = MIMEMultipart("alternative")
    message["subject"] = subject
    message["from"] = sender
    message["to"] = to

    if headers:
        for key, value in headers.items():
            message[key] = value

    if text_body:
        part1 = MIMEText(text_body, "plain")
        message.attach(part1)

    part2 = MIMEText(html_body, "html")
    message.attach(part2)

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return raw_message


def parse_email_address(email_str: str) -> str:
    """Extract email address from 'Name <email@example.com>' format."""
    if "<" in email_str and ">" in email_str:
        return email_str.split("<")[1].split(">")[0].strip()
    return email_str.strip()
