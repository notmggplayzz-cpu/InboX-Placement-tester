import os
import asyncio
import json
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urlencode

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database.models import GmailAccount
from app.utils.encryption import encrypt_token, decrypt_token
from app.utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/userinfo.email",
]


def get_google_oauth_url(state: str) -> str:
    """Generate Google OAuth authorization URL."""
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"


async def exchange_code_for_token(code: str) -> dict:
    """Exchange authorization code for access token."""
    loop = asyncio.get_event_loop()
    token_data = await loop.run_in_executor(None, _exchange_code_for_token_sync, code)

    # Get email from token if not included
    if not token_data.get("email"):
        email = await loop.run_in_executor(None, _get_email_from_access_token, token_data.get("access_token"))
        token_data["email"] = email

    return token_data


def _exchange_code_for_token_sync(code: str) -> dict:
    """Synchronous code exchange."""
    import requests

    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.google_redirect_uri,
    }

    try:
        response = requests.post(token_url, data=payload, timeout=settings.request_timeout_seconds)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to exchange code for token: {e}")
        raise


def _get_email_from_access_token(access_token: str) -> str:
    """Get email from access token using userinfo endpoint."""
    import requests

    if not access_token:
        return ""

    try:
        response = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo?access_token=" + access_token,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            email = data.get("email", "")
            logger.info(f"Got email from userinfo: {email}")
            return email
        else:
            logger.error(f"Userinfo failed: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Failed to get email: {e}")

    return ""


def save_oauth_account(
    db: Session,
    user_id: str,
    email: str,
    nickname: Optional[str],
    token_response: dict,
) -> GmailAccount:
    """Save Gmail account with OAuth tokens."""
    access_token = token_response.get("access_token")
    refresh_token = token_response.get("refresh_token")
    expires_in = token_response.get("expires_in", 3600)

    token_expiry = datetime.utcnow() + timedelta(seconds=expires_in - 60)

    encrypted_access = encrypt_token(access_token)
    encrypted_refresh = encrypt_token(refresh_token) if refresh_token else None

    existing = db.query(GmailAccount).filter(GmailAccount.email == email).first()
    if existing:
        existing.access_token = encrypted_access
        existing.refresh_token = encrypted_refresh
        existing.token_expiry = token_expiry
        existing.updated_at = datetime.utcnow()
        db.commit()
        logger.info(f"Updated Gmail account: {email}")
        return existing

    account = GmailAccount(
        user_id=user_id,
        email=email,
        nickname=nickname,
        access_token=encrypted_access,
        refresh_token=encrypted_refresh,
        token_expiry=token_expiry,
        is_active=True,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    logger.info(f"Created Gmail account: {email}")
    return account


async def refresh_access_token(account: GmailAccount) -> bool:
    """Refresh expired access token."""
    if not account.refresh_token:
        logger.warning(f"No refresh token for {account.email}")
        return False

    if account.token_expiry and account.token_expiry > datetime.utcnow() + timedelta(minutes=5):
        return True

    try:
        loop = asyncio.get_event_loop()
        success = await loop.run_in_executor(None, _refresh_token_sync, account)
        return success
    except Exception as e:
        logger.error(f"Failed to refresh token for {account.email}: {e}")
        return False


def _refresh_token_sync(account: GmailAccount) -> bool:
    """Synchronous token refresh."""
    import requests

    token_url = "https://oauth2.googleapis.com/token"

    try:
        refresh_token = decrypt_token(account.refresh_token)
        payload = {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        response = requests.post(token_url, data=payload, timeout=settings.request_timeout_seconds)
        response.raise_for_status()
        token_data = response.json()

        account.access_token = encrypt_token(token_data["access_token"])
        expires_in = token_data.get("expires_in", 3600)
        account.token_expiry = datetime.utcnow() + timedelta(seconds=expires_in - 60)

        logger.info(f"Refreshed token for {account.email}")
        return True
    except Exception as e:
        logger.error(f"Token refresh failed for {account.email}: {e}")
        return False


def get_credentials(account: GmailAccount) -> Credentials:
    """Get Google Credentials object from account."""
    access_token = decrypt_token(account.access_token)
    refresh_token = decrypt_token(account.refresh_token) if account.refresh_token else None

    credentials = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        scopes=SCOPES,
    )

    if credentials.expired and not credentials.refresh_token:
        raise RefreshError("Credentials expired and no refresh token available")

    return credentials
