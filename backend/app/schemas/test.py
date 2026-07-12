from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, model_validator

from app.database.models import GmailFolderEnum, TestStatusEnum


class TestCampaignCreate(BaseModel):
    campaign_name: str
    subject: str
    html_body: str
    plain_text_body: Optional[str] = None
    sender_email: EmailStr
    custom_headers: Optional[str] = None
    scheduled_time: Optional[datetime] = None


class TestCampaignResponse(BaseModel):
    id: int
    campaign_name: str
    subject: str
    sender_email: str
    status: TestStatusEnum
    total_accounts: int
    sent_time: Optional[datetime] = None
    completed_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TestResultResponse(BaseModel):
    id: int
    campaign_id: int
    account_id: int
    email: Optional[str] = None
    folder: GmailFolderEnum
    received_time: Optional[datetime] = None
    scanned_time: Optional[datetime] = None
    delivery_time_seconds: Optional[float] = None
    scan_time_seconds: Optional[float] = None
    labels: Optional[str] = None
    is_unread: bool
    is_starred: bool
    confidence: float
    error_message: Optional[str] = None
    retry_count: int
    created_at: datetime
    updated_at: datetime

    @model_validator(mode='after')
    def populate_email(self):
        # This will be called after the model is created
        # The account relationship should be loaded
        return self

    class Config:
        from_attributes = True


class TestStatisticsResponse(BaseModel):
    id: int
    campaign_id: int
    total_accounts: int
    inbox_count: int
    promotions_count: int
    social_count: int
    updates_count: int
    spam_count: int
    trash_count: int
    not_found_count: int
    inbox_percentage: float
    spam_percentage: float
    delivery_rate: float
    average_delivery_time: Optional[float] = None
    average_scan_time: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SendResultResponse(BaseModel):
    sent: int
    failed: int
    total: int
    campaign_id: int


class ScanResultResponse(BaseModel):
    account_id: int
    email: str
    folder: GmailFolderEnum
    scan_time: float
    confidence: float
    message_id: Optional[str] = None
    error: Optional[str] = None
