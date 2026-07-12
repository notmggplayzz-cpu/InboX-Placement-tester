from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class GmailAccountCreate(BaseModel):
    email: EmailStr
    nickname: Optional[str] = None


class GmailAccountUpdate(BaseModel):
    nickname: Optional[str] = None
    is_active: Optional[bool] = None


class GmailAccountResponse(BaseModel):
    id: int
    email: str
    nickname: Optional[str] = None
    is_active: bool
    last_sync: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
