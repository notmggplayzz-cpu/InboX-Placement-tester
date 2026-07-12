import asyncio
from datetime import datetime
from typing import Optional, List, Tuple
from concurrent.futures import ThreadPoolExecutor

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sqlalchemy.orm import Session

from app.database.models import GmailAccount, TestResult, GmailFolderEnum
from app.services.gmail_auth import get_credentials, refresh_access_token
from app.utils.logging import get_logger
from app.utils.email_parser import parse_gmail_message
from app.config import get_settings

logger = get_logger(__name__)
settings = get_settings()

GMAIL_LABELS = {
    "INBOX": GmailFolderEnum.INBOX,
    "CATEGORY_PROMOTIONS": GmailFolderEnum.PROMOTIONS,
    "CATEGORY_SOCIAL": GmailFolderEnum.SOCIAL,
    "CATEGORY_UPDATES": GmailFolderEnum.UPDATES,
    "SPAM": GmailFolderEnum.SPAM,
    "TRASH": GmailFolderEnum.TRASH,
}


async def scan_all_accounts(
    db: Session,
    campaign_id: int,
    subject: str,
    sender_email: str,
) -> List[dict]:
    """Scan all active Gmail accounts for test emails."""
    accounts = db.query(GmailAccount).filter(GmailAccount.is_active == True).all()

    scan_results = []
    executor = ThreadPoolExecutor(max_workers=settings.gmail_api_max_concurrent)
    loop = asyncio.get_event_loop()

    scan_tasks = []
    for account in accounts:
        task = loop.run_in_executor(
            executor,
            _scan_account,
            account,
            campaign_id,
            subject,
            sender_email,
            db,
        )
        scan_tasks.append(task)

    results = await asyncio.gather(*scan_tasks, return_exceptions=True)

    for result in results:
        if isinstance(result, Exception):
            logger.error(f"Scan error: {result}")
        else:
            scan_results.append(result)

    return scan_results


def _scan_account(
    account: GmailAccount,
    campaign_id: int,
    subject: str,
    sender_email: str,
    db: Session,
) -> dict:
    """Scan single Gmail account for test email."""
    start_time = datetime.utcnow()

    try:
        credentials = get_credentials(account)
        service = build("gmail", "v1", credentials=credentials)

        folder, message, confidence = _find_message(
            service, account, campaign_id, subject, sender_email
        )

        scanned_time = datetime.utcnow()
        scan_duration = (scanned_time - start_time).total_seconds()

        result = db.query(TestResult).filter(
            TestResult.campaign_id == campaign_id,
            TestResult.account_id == account.id,
        ).first()

        if result:
            result.email = account.email
            result.folder = folder
            result.scanned_time = scanned_time
            result.scan_time_seconds = scan_duration
            result.confidence = confidence

            if message:
                result.gmail_message_id = message["id"]
                result.message_id = message.get("message_id", "")
                result.received_time = message.get("received_time")
                result.labels = ",".join(message.get("labels", []))
                result.is_unread = "UNREAD" in message.get("labels", [])
                result.is_starred = "STARRED" in message.get("labels", [])

                if result.received_time and result.sent_time:
                    delivery_seconds = (result.received_time - result.sent_time).total_seconds()
                    result.delivery_time_seconds = max(0, delivery_seconds)

            db.commit()

            # Fetch fresh to get all data including email
            result = db.query(TestResult).filter(TestResult.id == result.id).first()
            logger.info(f"Scanned {account.email}: found in {folder}")
        else:
            logger.warning(f"No test result found for {account.email} in campaign {campaign_id}")

        account.last_sync = scanned_time
        db.commit()

        return {
            "account_id": account.id,
            "email": account.email,
            "folder": folder,
            "scan_time": scan_duration,
            "confidence": confidence,
            "message_id": message["id"] if message else None,
        }

    except Exception as e:
        logger.error(f"Failed to scan {account.email}: {e}")
        scanned_time = datetime.utcnow()
        scan_duration = (scanned_time - start_time).total_seconds()

        result = db.query(TestResult).filter(
            TestResult.campaign_id == campaign_id,
            TestResult.account_id == account.id,
        ).first()

        if result:
            result.error_message = str(e)
            result.scanned_time = scanned_time
            result.scan_time_seconds = scan_duration
            result.retry_count += 1
            db.commit()

        return {
            "account_id": account.id,
            "email": account.email,
            "folder": GmailFolderEnum.NOT_FOUND,
            "scan_time": scan_duration,
            "confidence": 0.0,
            "error": str(e),
        }


def _find_message(
    service,
    account: GmailAccount,
    campaign_id: int,
    subject: str,
    sender_email: str,
) -> Tuple[GmailFolderEnum, Optional[dict], float]:
    """Find test email in Gmail account."""
    try:
        query = f'from:"{sender_email}" subject:"{subject}"'
        results = service.users().messages().list(
            userId="me",
            q=query,
            maxResults=5,
        ).execute()

        messages = results.get("messages", [])

        if not messages:
            return GmailFolderEnum.NOT_FOUND, None, 0.0

        for msg_header in messages:
            msg_id = msg_header["id"]
            message = service.users().messages().get(
                userId="me",
                id=msg_id,
                format="full",
            ).execute()

            parsed = parse_gmail_message(message)
            labels = message.get("labelIds", [])

            folder = _detect_folder(labels)

            # Parse received time from headers
            date_str = parsed.get("date", "")
            received_time = _parse_email_date(date_str)

            return folder, {
                "id": msg_id,
                "message_id": parsed.get("message_id", ""),
                "labels": labels,
                "received_time": received_time,
            }, 1.0

        return GmailFolderEnum.NOT_FOUND, None, 0.0

    except HttpError as e:
        logger.error(f"Gmail API error for {account.email}: {e}")
        return GmailFolderEnum.NOT_FOUND, None, 0.0


def _detect_folder(labels: List[str]) -> GmailFolderEnum:
    """Detect folder from Gmail labels."""
    if "SPAM" in labels:
        return GmailFolderEnum.SPAM
    if "TRASH" in labels:
        return GmailFolderEnum.TRASH
    if "CATEGORY_PROMOTIONS" in labels:
        return GmailFolderEnum.PROMOTIONS
    if "CATEGORY_SOCIAL" in labels:
        return GmailFolderEnum.SOCIAL
    if "CATEGORY_UPDATES" in labels:
        return GmailFolderEnum.UPDATES
    if "INBOX" in labels:
        return GmailFolderEnum.INBOX

    return GmailFolderEnum.NOT_FOUND


def _parse_email_date(date_str: str) -> Optional[datetime]:
    """Parse email date string to datetime."""
    from email.utils import parsedate_to_datetime

    try:
        return parsedate_to_datetime(date_str)
    except (TypeError, ValueError):
        return None
