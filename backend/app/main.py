import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.config import get_settings
from app.database import init_db
from app.utils.logging import setup_logging, get_logger
from app.routers import accounts, tests

logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application")
    init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down application")


app = FastAPI(
    title="Email Inbox Placement Tester",
    description="Test email deliverability across your Gmail accounts",
    version="1.0.0",
    lifespan=lifespan,
)

setup_logging()

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.seoleads.me"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(accounts.router, prefix="/api/accounts", tags=["accounts"])
app.include_router(tests.router, prefix="/api/tests", tags=["tests"])


@app.get("/")
async def root():
    return {
        "message": "Email Inbox Placement Tester API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.api_workers,
    )
