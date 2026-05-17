"""Fixtures compartidos para toda la suite de pruebas.

Implementa: RNF04 — base de datos de prueba en ./data/test.db, aislada de producción,
            limpieza antes de cada test y eliminación al finalizar la sesión.
"""

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
# app.main importa app.models internamente; no re-importar aquí para evitar
# que "import app.models" sobreescriba el nombre "app" con el paquete.
from app.main import app as fastapi_app

# RNF04: BD de prueba en archivo separado, no en memoria
DB_PATH = "./data/test.db"
os.makedirs("./data", exist_ok=True)
TEST_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine_test = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

# Crear todas las tablas una sola vez al iniciar la sesión de pruebas
Base.metadata.create_all(bind=engine_test)


@pytest.fixture(autouse=True)
def limpiar_tablas():
    """RNF04: Limpia todas las filas de cada tabla antes de cada test."""
    yield
    with engine_test.connect() as conn:
        # Deshabilitar FK para poder truncar en cualquier orden
        conn.execute(text("PRAGMA foreign_keys=OFF"))
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
        conn.execute(text("PRAGMA foreign_keys=ON"))
        conn.commit()


@pytest.fixture(scope="session", autouse=True)
def eliminar_db_al_final():
    """RNF04: Elimina el archivo ./data/test.db al finalizar toda la sesión de pruebas."""
    yield
    engine_test.dispose()  # libera conexiones antes de borrar en Windows
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)


@pytest.fixture
def client():
    """TestClient de FastAPI con la sesión de BD de prueba inyectada."""
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    fastapi_app.dependency_overrides[get_db] = override_get_db
    with TestClient(fastapi_app) as test_client:
        yield test_client
    fastapi_app.dependency_overrides.clear()
