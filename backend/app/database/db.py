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
        logger.warning(f"Database schema creation failed (likely corrupted): {e}")
        logger.info("Dropping all tables and recreating...")
        try:
            Base.metadata.drop_all(bind=engine)
            Base.metadata.create_all(bind=engine)
            logger.info("Database reset successfully")
        except Exception as drop_error:
            logger.error(f"Failed to reset database: {drop_error}")
            raise

    seed_demo_accounts()


def seed_demo_accounts():
    from app.database.models import GmailAccount
    from app.utils.encryption import cipher_suite
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
                dummy_token = {
                    "access_token": "pending",
                    "refresh_token": "pending",
                    "expires_in": 3600,
                }

                account = GmailAccount(
                    email=email,
                    user_id="demo",
                    nickname=email.split("@")[0],
                    access_token_encrypted=cipher_suite.encrypt(
                        "pending".encode()
                    ),
                    refresh_token_encrypted=cipher_suite.encrypt(
                        "pending".encode()
                    ),
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
