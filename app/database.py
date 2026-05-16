"""Configuración de la base de datos SQLite con SQLAlchemy.

Implementa: RNF02 (Persistencia de datos), RNF03 (Convenciones de código)
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# RNF02: Archivo persistente local que sobrevive reinicios
SQLALCHEMY_DATABASE_URL = "sqlite:///./estudiantes.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)


# RNF02: Habilita claves foráneas en SQLite (desactivadas por defecto)
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Clase base para todos los modelos ORM del proyecto."""
    pass


def get_db():
    """Generador de sesión de base de datos para inyección de dependencias en FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
