from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db, GmailAccount
from app.schemas import GmailAccountCreate, GmailAccountResponse, GmailAccountUpdate
from app.services.gmail_auth import (
    get_google_oauth_url,
    exchange_code_for_token,
    save_oauth_account,
)
from app.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/oauth-url")
async def get_oauth_url(state: str = Query(...)):
    """Get Google OAuth authorization URL."""
    try:
        url = get_google_oauth_url(state)
        return {"url": url}
    except Exception as e:
        logger.error(f"Failed to generate OAuth URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/callback", include_in_schema=False)
async def oauth_callback_get(
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db),
):
    """Handle OAuth callback from Google (GET)."""
    try:
        token_response = await exchange_code_for_token(code)
        user_id = state

        # Get email from token
        import asyncio
        loop = asyncio.get_event_loop()
        email = await loop.run_in_executor(
            None, _get_email_from_token, token_response.get("access_token")
        )

        logger.info(f"OAuth callback - email: {email}, token keys: {list(token_response.keys())}")

        if not email:
            raise Exception("Could not retrieve email from Google. Check scopes and API permissions.")

        account = save_oauth_account(
            db=db,
            user_id=user_id,
            email=email,
            nickname=None,
            token_response=token_response,
        )

        return {"account_id": account.id, "email": account.email}

    except Exception as e:
        logger.error(f"OAuth callback failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


def _get_email_from_token(access_token: str) -> str:
    """Get email from access token."""
    import requests

    if not access_token:
        logger.error("No access token provided")
        return ""

    try:
        # Use Google's userinfo v2 endpoint
        response = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10
        )

        logger.info(f"Userinfo response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            logger.info(f"Userinfo data: {data}")
            email = data.get("email", "")
            if email:
                return email
        else:
            logger.error(f"Userinfo request failed: {response.status_code} - {response.text}")

    except Exception as e:
        logger.error(f"Failed to get email from userinfo: {e}", exc_info=True)

    return ""


@router.get("", response_model=List[GmailAccountResponse])
async def list_accounts(db: Session = Depends(get_db)):
    """List all connected Gmail accounts."""
    try:
        accounts = db.query(GmailAccount).filter(
            GmailAccount.is_active == True
        ).all()
        return accounts
    except Exception as e:
        logger.error(f"Failed to list accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{account_id}", response_model=GmailAccountResponse)
async def get_account(account_id: int, db: Session = Depends(get_db)):
    """Get specific Gmail account details."""
    try:
        account = db.query(GmailAccount).filter(
            GmailAccount.id == account_id
        ).first()

        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        return account

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{account_id}", response_model=GmailAccountResponse)
async def update_account(
    account_id: int,
    account_update: GmailAccountUpdate,
    db: Session = Depends(get_db),
):
    """Update Gmail account details."""
    try:
        account = db.query(GmailAccount).filter(
            GmailAccount.id == account_id
        ).first()

        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        if account_update.nickname is not None:
            account.nickname = account_update.nickname

        if account_update.is_active is not None:
            account.is_active = account_update.is_active

        db.commit()
        db.refresh(account)

        return account

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{account_id}")
async def delete_account(account_id: int, db: Session = Depends(get_db)):
    """Delete Gmail account and associated data."""
    try:
        account = db.query(GmailAccount).filter(
            GmailAccount.id == account_id
        ).first()

        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        db.delete(account)
        db.commit()

        return {"message": "Account deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete account: {e}")
        raise HTTPException(status_code=500, detail=str(e))
