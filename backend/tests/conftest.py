import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database.models import Base
from app.database import get_db
from app.main import app


@pytest.fixture(scope="function")
def test_db():
    """Create a test database."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    yield db

    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_client(test_db):
    """Create a test client."""
    def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()
