from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Index,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class GmailFolderEnum(str, PyEnum):
    INBOX = "INBOX"
    PROMOTIONS = "CATEGORY_PROMOTIONS"
    SOCIAL = "CATEGORY_SOCIAL"
    UPDATES = "CATEGORY_UPDATES"
    SPAM = "SPAM"
    TRASH = "TRASH"
    NOT_FOUND = "NOT_FOUND"


class TestStatusEnum(str, PyEnum):
    DRAFT = "draft"
    SENDING = "sending"
    SENT = "sent"
    SCANNING = "scanning"
    COMPLETED = "completed"
    FAILED = "failed"


class GmailAccount(Base):
    __tablename__ = "gmail_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    nickname = Column(String, nullable=True)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_expiry = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    last_sync = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tests = relationship("TestResult", back_populates="account", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_user_id_email", "user_id", "email"),
        Index("idx_is_active", "is_active"),
    )


class TestCampaign(Base):
    __tablename__ = "test_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    campaign_name = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    html_body = Column(Text, nullable=False)
    plain_text_body = Column(Text, nullable=True)
    sender_email = Column(String, nullable=False)
    custom_headers = Column(Text, nullable=True)
    status = Column(Enum(TestStatusEnum), default=TestStatusEnum.DRAFT, index=True)
    scheduled_time = Column(DateTime, nullable=True)
    sent_time = Column(DateTime, nullable=True)
    completed_time = Column(DateTime, nullable=True)
    total_accounts = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    results = relationship("TestResult", back_populates="campaign", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_status", "status"),
    )


class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("test_campaigns.id"), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("gmail_accounts.id"), nullable=False, index=True)
    email = Column(String, nullable=True)
    folder = Column(Enum(GmailFolderEnum), default=GmailFolderEnum.NOT_FOUND, nullable=False)
    message_id = Column(String, nullable=True, index=True)
    gmail_message_id = Column(String, nullable=True, unique=True)
    received_time = Column(DateTime, nullable=True)
    scanned_time = Column(DateTime, nullable=True)
    delivery_time_seconds = Column(Float, nullable=True)
    scan_time_seconds = Column(Float, nullable=True)
    labels = Column(Text, nullable=True)
    is_unread = Column(Boolean, default=True)
    is_starred = Column(Boolean, default=False)
    confidence = Column(Float, default=1.0)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    campaign = relationship("TestCampaign", back_populates="results")
    account = relationship("GmailAccount", back_populates="tests")

    def get_email(self):
        return self.account.email if self.account else None

    __table_args__ = (
        UniqueConstraint("campaign_id", "account_id", name="uq_campaign_account"),
        Index("idx_folder", "folder"),
        Index("idx_gmail_message_id", "gmail_message_id"),
    )


class ScanSession(Base):
    __tablename__ = "scan_sessions"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("test_campaigns.id"), nullable=False, index=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    total_scanned = Column(Integer, default=0)
    found_count = Column(Integer, default=0)
    not_found_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    average_delivery_time = Column(Float, nullable=True)
    average_scan_time = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)

    __table_args__ = (
        Index("idx_campaign_id", "campaign_id"),
    )


class TestStatistics(Base):
    __tablename__ = "test_statistics"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("test_campaigns.id"), nullable=False, unique=True)
    total_accounts = Column(Integer, default=0)
    inbox_count = Column(Integer, default=0)
    promotions_count = Column(Integer, default=0)
    social_count = Column(Integer, default=0)
    updates_count = Column(Integer, default=0)
    spam_count = Column(Integer, default=0)
    trash_count = Column(Integer, default=0)
    not_found_count = Column(Integer, default=0)
    inbox_percentage = Column(Float, default=0.0)
    spam_percentage = Column(Float, default=0.0)
    delivery_rate = Column(Float, default=0.0)
    average_delivery_time = Column(Float, nullable=True)
    average_scan_time = Column(Float, nullable=True)
    fastest_delivery_time = Column(Float, nullable=True)
    slowest_delivery_time = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_campaign_id", "campaign_id"),
    )
