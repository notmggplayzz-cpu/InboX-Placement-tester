import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

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
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(accounts.router, prefix="/api/accounts", tags=["accounts"])
app.include_router(tests.router, prefix="/api/tests", tags=["tests"])


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Serve static files
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    @app.get("/{full_path:path}")
    async def serve_static(full_path: str):
        """Serve static files or index.html for SPA routing"""
        file_path = static_dir / full_path

        if file_path.is_file():
            return FileResponse(file_path)

        # Serve index.html for SPA routing
        index_path = static_dir / "index.html"
        if index_path.exists():
            return FileResponse(index_path)

        return {"error": "File not found"}


@app.get("/")
async def root():
    """Serve index.html at root"""
    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "Email Inbox Placement Tester API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.api_workers,
    )
# Force redeploy
