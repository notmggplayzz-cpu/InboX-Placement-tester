import asyncio
from datetime import datetime
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sqlalchemy.orm import Session

from app.database.models import GmailAccount, TestCampaign, TestResult, TestStatusEnum
from app.services.gmail_auth import get_credentials, refresh_access_token
from app.utils.email_parser import create_mime_message
from app.utils.logging import get_logger
from app.config import get_settings

logger = get_logger(__name__)
settings = get_settings()


async def send_to_all_accounts(
    db: Session,
    campaign: TestCampaign,
    recipient_accounts: List[GmailAccount],
) -> dict:
    """Send test email to all recipient accounts."""
    campaign.status = TestStatusEnum.SENDING
    campaign.sent_time = None
    db.commit()

    executor = ThreadPoolExecutor(max_workers=settings.gmail_api_max_concurrent)
    loop = asyncio.get_event_loop()

    send_tasks = []
    for account in recipient_accounts:
        task = loop.run_in_executor(
            executor,
            _send_to_account,
            account,
            campaign,
            db,
        )
        send_tasks.append(task)

    results = await asyncio.gather(*send_tasks, return_exceptions=True)

    sent_count = 0
    failed_count = 0

    for result in results:
        if isinstance(result, Exception):
            logger.error(f"Send error: {result}")
            failed_count += 1
        elif result.get("success"):
            sent_count += 1
        else:
            failed_count += 1

    now = datetime.utcnow()
    campaign.status = TestStatusEnum.SENT
    campaign.sent_time = now
    campaign.total_accounts = len(recipient_accounts)
    db.commit()

    return {
        "sent": sent_count,
        "failed": failed_count,
        "total": len(recipient_accounts),
        "campaign_id": campaign.id,
    }


def _send_to_account(
    account: GmailAccount,
    campaign: TestCampaign,
    db: Session,
) -> dict:
    """Send test email to single account."""
    try:
        refreshed = refresh_access_token(account)
        if not refreshed:
            raise Exception("Failed to refresh access token")

        credentials = get_credentials(account)
        service = build("gmail", "v1", credentials=credentials)

        raw_message = create_mime_message(
            sender=campaign.sender_email,
            to=account.email,
            subject=campaign.subject,
            html_body=campaign.html_body,
            text_body=campaign.plain_text_body,
            headers=_parse_custom_headers(campaign.custom_headers),
        )

        message = {"raw": raw_message}
        sent_message = service.users().messages().send(userId="me", body=message).execute()

        test_result = db.query(TestResult).filter(
            TestResult.campaign_id == campaign.id,
            TestResult.account_id == account.id,
        ).first()

        if not test_result:
            test_result = TestResult(
                campaign_id=campaign.id,
                account_id=account.id,
            )
            db.add(test_result)

        test_result.sent_time = datetime.utcnow()
        test_result.error_message = None
        db.commit()

        logger.info(f"Sent test email to {account.email}")

        return {
            "success": True,
            "account_id": account.id,
            "email": account.email,
            "message_id": sent_message.get("id"),
        }

    except Exception as e:
        logger.error(f"Failed to send to {account.email}: {e}")

        test_result = db.query(TestResult).filter(
            TestResult.campaign_id == campaign.id,
            TestResult.account_id == account.id,
        ).first()

        if not test_result:
            test_result = TestResult(
                campaign_id=campaign.id,
                account_id=account.id,
            )
            db.add(test_result)

        test_result.error_message = str(e)
        test_result.sent_time = None
        db.commit()

        return {
            "success": False,
            "account_id": account.id,
            "email": account.email,
            "error": str(e),
        }


def _parse_custom_headers(headers_json: Optional[str]) -> dict:
    """Parse custom headers from JSON string."""
    if not headers_json:
        return {}

    try:
        import json
        return json.loads(headers_json)
    except Exception as e:
        logger.warning(f"Failed to parse custom headers: {e}")
        return {}


async def send_via_smtp(
    sender_email: str,
    sender_password: str,
    to_email: str,
    subject: str,
    html_body: str,
    text_body: Optional[str] = None,
) -> bool:
    """Send email via SMTP (alternative to Gmail API)."""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    try:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            _send_smtp_sync,
            sender_email,
            sender_password,
            to_email,
            subject,
            html_body,
            text_body,
        )
    except Exception as e:
        logger.error(f"SMTP send failed: {e}")
        return False


def _send_smtp_sync(
    sender_email: str,
    sender_password: str,
    to_email: str,
    subject: str,
    html_body: str,
    text_body: Optional[str] = None,
) -> bool:
    """Synchronous SMTP send."""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = to_email

    if text_body:
        part1 = MIMEText(text_body, "plain")
        message.attach(part1)

    part2 = MIMEText(html_body, "html")
    message.attach(part2)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, message.as_string())

    return True
