from collections.abc import Generator
from sqlmodel import Session, SQLModel, create_engine
from core.config import settings

# Engine de SQLAlchemy/SQLModel conectado a PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,  # Reconexión automática si el socket se cierra
)


def init_db() -> None:
    """Crea las tablas en PostgreSQL si aún no existen."""
    try:
        SQLModel.metadata.create_all(engine)
        print("Base de datos PostgreSQL inicializada exitosamente.")
    except Exception as exc:
        print(f"Aviso al conectar con PostgreSQL: {exc}")


def get_session() -> Generator[Session, None, None]:
    """Generador de sesiones para inyección de dependencias en FastAPI."""
    with Session(engine) as session:
        yield session
