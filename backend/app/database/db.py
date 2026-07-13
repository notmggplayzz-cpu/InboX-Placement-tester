from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.config import get_settings

settings = get_settings()

# Database engine configuration
if settings.database_url.startswith("sqlite"):
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_engine(
        settings.database_url,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_pre_ping=True,
        pool_recycle=3600,
    )

# Enable foreign keys for SQLite
if settings.database_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app.database.models import Base
    from app.utils.logging import get_logger
    logger = get_logger(__name__)

    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        if "already exists" in str(e):
            logger.info("Database schema already exists, skipping creation")
        else:
            logger.error(f"Database initialization error: {e}")
            raise


def seed_demo_accounts():
    from app.database.models import GmailAccount
    from app.utils.encryption import encrypt_token
    from datetime import datetime, timedelta

    demo_emails = [
        "these-kaifmerchant81@gmail.com",
        "notmggplayzz@gmail.com",
        "chrismareno67@gmail.com",
        "trendyworldnewss@gmail.com",
        "chatgod48@gmail.com",
    ]

    db = SessionLocal()
    try:
        for email in demo_emails:
            existing = db.query(GmailAccount).filter(
                GmailAccount.email == email
            ).first()

            if not existing:
                account = GmailAccount(
                    email=email,
                    user_id="demo",
                    nickname=email.split("@")[0],
                    access_token_encrypted=encrypt_token("pending"),
                    refresh_token_encrypted=encrypt_token("pending"),
                    token_expiry=datetime.utcnow() + timedelta(hours=1),
                    is_active=True,
                )
                db.add(account)

        db.commit()
    except Exception as e:
        db.rollback()
        from app.utils.logging import get_logger
        logger = get_logger(__name__)
        logger.error(f"Error seeding demo accounts: {e}")
    finally:
        db.close()
