"""Funciones CRUD para la entidad Estudiante.

Implementa: RF01 (crear), RF02 (obtener por ID), RF03 (buscar por nombre),
            RF04 (actualizar), RF05 (eliminar), RF06 (listar),
            RF10 (validaciones de unicidad), RNF01 (queries optimizadas con índices)
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.estudiante import Estudiante
from app.schemas.estudiante import EstudianteCreate, EstudianteUpdate


def crear_estudiante(db: Session, datos: EstudianteCreate) -> Estudiante:
    """RF01: Crea un nuevo estudiante en la base de datos."""
    estudiante = Estudiante(**datos.model_dump())
    db.add(estudiante)
    db.commit()
    db.refresh(estudiante)
    return estudiante


def obtener_estudiante_por_id(db: Session, estudiante_id: int) -> Estudiante | None:
    """RF02: Retorna un estudiante por su ID, o None si no existe."""
    return db.query(Estudiante).filter(Estudiante.id == estudiante_id).first()


def obtener_estudiantes(db: Session, skip: int = 0, limit: int = 100, nombre: str | None = None) -> list[Estudiante]:
    """RF06: Lista todos los estudiantes con paginación.
    RF03: Si se pasa `nombre`, filtra por coincidencia parcial case-insensitive.
    """
    query = db.query(Estudiante)
    if nombre:
        query = query.filter(func.lower(Estudiante.nombre).contains(nombre.lower()))
    return query.offset(skip).limit(limit).all()


def actualizar_estudiante(db: Session, estudiante: Estudiante, datos: EstudianteUpdate) -> Estudiante:
    """RF04: Actualiza solo los campos enviados (PATCH parcial)."""
    campos = datos.model_dump(exclude_unset=True)
    for campo, valor in campos.items():
        setattr(estudiante, campo, valor)
    db.commit()
    db.refresh(estudiante)
    return estudiante


def eliminar_estudiante(db: Session, estudiante: Estudiante) -> None:
    """RF05: Elimina el estudiante y sus inscripciones (cascade definido en el modelo)."""
    db.delete(estudiante)
    db.commit()


def existe_email(db: Session, email: str, excluir_id: int | None = None) -> bool:
    """RF10: Verifica si el email ya está registrado por otro estudiante."""
    query = db.query(Estudiante).filter(func.lower(Estudiante.email) == email.lower())
    if excluir_id is not None:
        query = query.filter(Estudiante.id != excluir_id)
    return query.first() is not None


def existe_codigo(db: Session, codigo: str, excluir_id: int | None = None) -> bool:
    """RF10: Verifica si el código estudiantil ya está registrado por otro estudiante."""
    query = db.query(Estudiante).filter(func.lower(Estudiante.codigo) == codigo.lower())
    if excluir_id is not None:
        query = query.filter(Estudiante.id != excluir_id)
    return query.first() is not None
