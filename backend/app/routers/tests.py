from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import (
    get_db,
    TestCampaign,
    TestResult,
    TestStatistics,
    GmailAccount,
    TestStatusEnum,
)
from app.schemas import (
    TestCampaignCreate,
    TestCampaignResponse,
    TestResultResponse,
    TestStatisticsResponse,
    SendResultResponse,
)
from app.services.gmail_sender import send_to_all_accounts
from app.services.gmail_scanner import scan_all_accounts
from app.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("", response_model=TestCampaignResponse)
async def create_test(
    test: TestCampaignCreate,
    db: Session = Depends(get_db),
):
    """Create a new test campaign."""
    try:
        campaign = TestCampaign(
            user_id="default_user",
            campaign_name=test.campaign_name,
            subject=test.subject,
            html_body=test.html_body,
            plain_text_body=test.plain_text_body,
            sender_email=test.sender_email,
            custom_headers=test.custom_headers,
            scheduled_time=test.scheduled_time,
        )

        db.add(campaign)
        db.commit()
        db.refresh(campaign)

        logger.info(f"Created test campaign: {campaign.id}")

        return campaign

    except Exception as e:
        logger.error(f"Failed to create test: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[TestCampaignResponse])
async def list_tests(
    status: str = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    db: Session = Depends(get_db),
):
    """List all test campaigns."""
    try:
        query = db.query(TestCampaign).order_by(TestCampaign.created_at.desc())

        if status:
            query = query.filter(TestCampaign.status == status)

        campaigns = query.limit(limit).offset(offset).all()
        return campaigns

    except Exception as e:
        logger.error(f"Failed to list tests: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{campaign_id}", response_model=TestCampaignResponse)
async def get_test(campaign_id: int, db: Session = Depends(get_db)):
    """Get test campaign details."""
    try:
        campaign = db.query(TestCampaign).filter(
            TestCampaign.id == campaign_id
        ).first()

        if not campaign:
            raise HTTPException(status_code=404, detail="Test campaign not found")

        return campaign

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get test: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{campaign_id}/send", response_model=SendResultResponse)
async def send_test(
    campaign_id: int,
    db: Session = Depends(get_db),
):
    """Send test email to all active accounts."""
    try:
        campaign = db.query(TestCampaign).filter(
            TestCampaign.id == campaign_id
        ).first()

        if not campaign:
            raise HTTPException(status_code=404, detail="Test campaign not found")

        accounts = db.query(GmailAccount).filter(
            GmailAccount.is_active == True
        ).all()

        if not accounts:
            raise HTTPException(status_code=400, detail="No active Gmail accounts")

        for account in accounts:
            test_result = db.query(TestResult).filter(
                TestResult.campaign_id == campaign_id,
                TestResult.account_id == account.id,
            ).first()

            if not test_result:
                test_result = TestResult(
                    campaign_id=campaign_id,
                    account_id=account.id,
                )
                db.add(test_result)

        db.commit()

        result = await send_to_all_accounts(db, campaign, accounts)

        logger.info(f"Sent test emails for campaign {campaign_id}: {result}")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send test: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{campaign_id}/scan")
async def scan_test(campaign_id: int, db: Session = Depends(get_db)):
    """Scan all accounts for test email."""
    try:
        campaign = db.query(TestCampaign).filter(
            TestCampaign.id == campaign_id
        ).first()

        if not campaign:
            raise HTTPException(status_code=404, detail="Test campaign not found")

        campaign.status = TestStatusEnum.SCANNING
        db.commit()

        results = await scan_all_accounts(
            db,
            campaign_id,
            campaign.subject,
            campaign.sender_email,
        )

        campaign.status = TestStatusEnum.COMPLETED
        campaign.completed_time = datetime.utcnow()
        db.commit()

        _update_statistics(db, campaign_id)

        logger.info(f"Completed scanning for campaign {campaign_id}")

        return {
            "campaign_id": campaign_id,
            "scanned": len(results),
            "completed_at": campaign.completed_time,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to scan test: {e}")
        campaign = db.query(TestCampaign).filter(
            TestCampaign.id == campaign_id
        ).first()
        if campaign:
            campaign.status = TestStatusEnum.FAILED
            db.commit()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{campaign_id}/results", response_model=List[TestResultResponse])
async def get_test_results(campaign_id: int, db: Session = Depends(get_db)):
    """Get test results for a campaign."""
    try:
        campaign = db.query(TestCampaign).filter(
            TestCampaign.id == campaign_id
        ).first()

        if not campaign:
            raise HTTPException(status_code=404, detail="Test campaign not found")

        results = db.query(TestResult).filter(
            TestResult.campaign_id == campaign_id
        ).all()

        return results

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get results: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{campaign_id}/statistics", response_model=TestStatisticsResponse)
async def get_test_statistics(campaign_id: int, db: Session = Depends(get_db)):
    """Get statistics for a test campaign."""
    try:
        stats = db.query(TestStatistics).filter(
            TestStatistics.campaign_id == campaign_id
        ).first()

        if not stats:
            raise HTTPException(status_code=404, detail="Statistics not found")

        return stats

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{campaign_id}")
async def delete_test(campaign_id: int, db: Session = Depends(get_db)):
    """Delete a test campaign."""
    try:
        campaign = db.query(TestCampaign).filter(
            TestCampaign.id == campaign_id
        ).first()

        if not campaign:
            raise HTTPException(status_code=404, detail="Test campaign not found")

        db.delete(campaign)
        db.commit()

        return {"message": "Test campaign deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete test: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/browse/emails")
async def browse_emails(account_id: int = None, db: Session = Depends(get_db)):
    """Browse all emails in Gmail account."""
    try:
        from googleapiclient.discovery import build
        from app.services.gmail_auth import get_credentials

        if not account_id:
            account = db.query(GmailAccount).filter(
                GmailAccount.is_active == True
            ).first()
            if not account:
                raise HTTPException(status_code=400, detail="No Gmail accounts connected")
        else:
            account = db.query(GmailAccount).filter(
                GmailAccount.id == account_id
            ).first()
            if not account:
                raise HTTPException(status_code=404, detail="Account not found")

        credentials = get_credentials(account)
        service = build("gmail", "v1", credentials=credentials)

        # Get recent emails
        results = service.users().messages().list(
            userId="me",
            maxResults=50,
            q="is:unread OR is:important OR newer_than:7d"
        ).execute()

        messages = results.get("messages", [])
        emails = []

        for msg_header in messages[:20]:
            try:
                message = service.users().messages().get(
                    userId="me",
                    id=msg_header["id"],
                    format="full"
                ).execute()

                headers = message.get("payload", {}).get("headers", [])
                header_dict = {h.get("name", "").lower(): h.get("value", "") for h in headers}

                labels = message.get("labelIds", [])

                # Determine folder
                folder = "Inbox"
                if "SPAM" in labels:
                    folder = "Spam"
                elif "CATEGORY_PROMOTIONS" in labels:
                    folder = "Promotions"
                elif "CATEGORY_SOCIAL" in labels:
                    folder = "Social"
                elif "CATEGORY_UPDATES" in labels:
                    folder = "Updates"
                elif "TRASH" in labels:
                    folder = "Trash"

                emails.append({
                    "id": msg_header["id"],
                    "from": header_dict.get("from", "Unknown"),
                    "subject": header_dict.get("subject", "(No subject)"),
                    "date": header_dict.get("date", ""),
                    "folder": folder,
                    "labels": ",".join(labels),
                    "snippet": message.get("snippet", ""),
                })
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                continue

        return {
            "account": account.email,
            "emails": emails
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to browse emails: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _update_statistics(db: Session, campaign_id: int):
    """Calculate and update statistics for a campaign."""
    results = db.query(TestResult).filter(
        TestResult.campaign_id == campaign_id
    ).all()

    if not results:
        return

    from app.database.models import GmailFolderEnum

    folder_counts = {
        GmailFolderEnum.INBOX: 0,
        GmailFolderEnum.PROMOTIONS: 0,
        GmailFolderEnum.SOCIAL: 0,
        GmailFolderEnum.UPDATES: 0,
        GmailFolderEnum.SPAM: 0,
        GmailFolderEnum.TRASH: 0,
        GmailFolderEnum.NOT_FOUND: 0,
    }

    delivery_times = []
    scan_times = []

    for result in results:
        folder_counts[result.folder] += 1
        if result.delivery_time_seconds:
            delivery_times.append(result.delivery_time_seconds)
        if result.scan_time_seconds:
            scan_times.append(result.scan_time_seconds)

    total = len(results)
    inbox_count = folder_counts[GmailFolderEnum.INBOX]
    spam_count = folder_counts[GmailFolderEnum.SPAM]
    not_found = folder_counts[GmailFolderEnum.NOT_FOUND]

    stats = db.query(TestStatistics).filter(
        TestStatistics.campaign_id == campaign_id
    ).first()

    if not stats:
        stats = TestStatistics(campaign_id=campaign_id)
        db.add(stats)

    stats.total_accounts = total
    stats.inbox_count = inbox_count
    stats.promotions_count = folder_counts[GmailFolderEnum.PROMOTIONS]
    stats.social_count = folder_counts[GmailFolderEnum.SOCIAL]
    stats.updates_count = folder_counts[GmailFolderEnum.UPDATES]
    stats.spam_count = spam_count
    stats.trash_count = folder_counts[GmailFolderEnum.TRASH]
    stats.not_found_count = not_found
    stats.inbox_percentage = (inbox_count / total * 100) if total > 0 else 0
    stats.spam_percentage = (spam_count / total * 100) if total > 0 else 0
    stats.delivery_rate = ((total - not_found) / total * 100) if total > 0 else 0

    if delivery_times:
        stats.average_delivery_time = sum(delivery_times) / len(delivery_times)
        stats.fastest_delivery_time = min(delivery_times)
        stats.slowest_delivery_time = max(delivery_times)

    if scan_times:
        stats.average_scan_time = sum(scan_times) / len(scan_times)

    db.commit()
