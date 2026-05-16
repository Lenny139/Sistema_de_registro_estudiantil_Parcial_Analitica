"""Punto de entrada principal de la aplicación FastAPI.

Implementa: RNF02 (inicialización automática de tablas),
            RNF05 (Swagger UI en /docs, ReDoc en /redoc),
            RNF03 (estructura de capas, convenciones)
"""

from fastapi import FastAPI
from app.database import engine, Base
from app.routers import estudiantes, materias

# RNF02: Importar modelos para que SQLAlchemy los registre antes de crear tablas
import app.models  # noqa: F401

# RNF05: Metadatos para la documentación automática
app = FastAPI(
    title="Sistema de Registro de Estudiantes",
    description=(
        "API RESTful para gestión académica de estudiantes. "
        "Permite registrar estudiantes, administrar materias e inscripciones. "
        "Desarrollado bajo el marco SDD (Specification Driven Development)."
    ),
    version="1.0.0",
    contact={"name": "Equipo de Desarrollo", "email": "dev@universidad.edu.co"},
    license_info={"name": "MIT"},
    docs_url="/docs",      # RNF05: Swagger UI
    redoc_url="/redoc",    # RNF05: ReDoc
)


# RNF02: Crear tablas automáticamente si no existen al iniciar la aplicación
@app.on_event("startup")
def inicializar_base_de_datos():
    """Crea todas las tablas definidas en los modelos si no existen."""
    Base.metadata.create_all(bind=engine)


# Registrar routers
app.include_router(estudiantes.router)
app.include_router(materias.router)


@app.get("/", tags=["Health"], summary="Estado de la API")
def health_check():
    """Verifica que la API está en funcionamiento."""
    return {
        "estado": "activo",
        "version": "1.0.0",
        "documentacion": "/docs",
    }
