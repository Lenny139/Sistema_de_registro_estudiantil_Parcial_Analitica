"""Funciones CRUD para Materia e Inscripcion.

Implementa: RF07 (inscribir estudiante), RF08 (materias por estudiante),
            RF09 (crear, listar, eliminar materias),
            RF10 (código único de materia), RNF02 (integridad referencial)
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.materia import Materia
from app.models.inscripcion import Inscripcion
from app.schemas.materia import MateriaCreate


def crear_materia(db: Session, datos: MateriaCreate) -> Materia:
    """RF09: Crea una nueva materia en la base de datos."""
    materia = Materia(**datos.model_dump())
    db.add(materia)
    db.commit()
    db.refresh(materia)
    return materia


def obtener_materia_por_id(db: Session, materia_id: int) -> Materia | None:
    """RF09: Retorna una materia por su ID, o None si no existe."""
    return db.query(Materia).filter(Materia.id == materia_id).first()


def obtener_materias(db: Session, skip: int = 0, limit: int = 100) -> list[Materia]:
    """RF09: Lista todas las materias con paginación opcional."""
    return db.query(Materia).offset(skip).limit(limit).all()


def eliminar_materia(db: Session, materia: Materia) -> None:
    """RF09: Elimina una materia (cascade elimina inscripciones asociadas)."""
    db.delete(materia)
    db.commit()


def existe_codigo_materia(db: Session, codigo: str, excluir_id: int | None = None) -> bool:
    """RF10: Verifica si el código de materia ya está registrado."""
    query = db.query(Materia).filter(func.lower(Materia.codigo) == codigo.lower())
    if excluir_id is not None:
        query = query.filter(Materia.id != excluir_id)
    return query.first() is not None


def inscribir_estudiante(db: Session, estudiante_id: int, materia_id: int) -> Inscripcion:
    """RF07: Crea la inscripción entre un estudiante y una materia."""
    inscripcion = Inscripcion(estudiante_id=estudiante_id, materia_id=materia_id)
    db.add(inscripcion)
    db.commit()
    db.refresh(inscripcion)
    return inscripcion


def obtener_materias_de_estudiante(db: Session, estudiante_id: int) -> list[Materia]:
    """RF08: Retorna todas las materias en las que está inscrito un estudiante."""
    return (
        db.query(Materia)
        .join(Inscripcion, Inscripcion.materia_id == Materia.id)
        .filter(Inscripcion.estudiante_id == estudiante_id)
        .all()
    )


def existe_inscripcion(db: Session, estudiante_id: int, materia_id: int) -> bool:
    """RF07: Verifica si ya existe la inscripción para evitar duplicados."""
    return (
        db.query(Inscripcion)
        .filter(
            Inscripcion.estudiante_id == estudiante_id,
            Inscripcion.materia_id == materia_id,
        )
        .first()
        is not None
    )
