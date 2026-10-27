import sys
from pathlib import Path

# Asegurar que el directorio raíz del bff esté en el sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool
from fastapi.testclient import TestClient

from main import app
from core.database import get_session
from core.database.models import CibaTransaction


@pytest.fixture(name="session")
def session_fixture():
    # Base de datos SQLite en memoria para tests aislados
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
