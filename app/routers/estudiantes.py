"""Endpoints REST para la gestión de estudiantes.

Implementa: RF01 (POST /estudiantes), RF02 (GET /estudiantes/{id}),
            RF03 (GET /estudiantes?nombre=), RF04 (PATCH /estudiantes/{id}),
            RF05 (DELETE /estudiantes/{id}), RF06 (GET /estudiantes),
            RF07 (POST /estudiantes/{id}/materias/{materia_id}),
            RF08 (GET /estudiantes/{id}/materias),
            RF10 (409 en duplicados), RNF05 (documentación Swagger)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.estudiante import EstudianteCreate, EstudianteUpdate, EstudianteResponse
from app.schemas.materia import MateriaResponse
from app.crud import estudiante as crud_est
from app.crud import materia as crud_mat

router = APIRouter(prefix="/estudiantes", tags=["Estudiantes"])


@router.post(
    "/",
    response_model=EstudianteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="RF01 — Registrar nuevo estudiante",
    responses={
        409: {"description": "Email o código ya registrado"},
        422: {"description": "Datos inválidos o campos faltantes"},
    },
)
def crear_estudiante(datos: EstudianteCreate, db: Session = Depends(get_db)):
    """Crea un nuevo estudiante. El email y el código deben ser únicos."""
    # RF10: validar unicidad antes de persistir
    if crud_est.existe_email(db, datos.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El email ya está registrado")
    if crud_est.existe_codigo(db, datos.codigo):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El código estudiantil ya está registrado")
    return crud_est.crear_estudiante(db, datos)


@router.get(
    "/",
    response_model=list[EstudianteResponse],
    status_code=status.HTTP_200_OK,
    summary="RF06 — Listar estudiantes / RF03 — Buscar por nombre",
    responses={200: {"description": "Lista de estudiantes (puede estar vacía)"}},
)
def listar_estudiantes(
    nombre: Optional[str] = Query(None, description="Filtro parcial por nombre (case-insensitive)"),
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=500, description="Máximo de registros a retornar"),
    db: Session = Depends(get_db),
):
    """Retorna todos los estudiantes. Con el parámetro `nombre` filtra por coincidencia parcial."""
    return crud_est.obtener_estudiantes(db, skip=skip, limit=limit, nombre=nombre)


@router.get(
    "/{estudiante_id}",
    response_model=EstudianteResponse,
    status_code=status.HTTP_200_OK,
    summary="RF02 — Obtener estudiante por ID",
    responses={404: {"description": "Estudiante no encontrado"}},
)
def obtener_estudiante(estudiante_id: int, db: Session = Depends(get_db)):
    """Retorna los datos completos de un estudiante a partir de su ID."""
    estudiante = crud_est.obtener_estudiante_por_id(db, estudiante_id)
    if not estudiante:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estudiante no encontrado")
    return estudiante


@router.patch(
    "/{estudiante_id}",
    response_model=EstudianteResponse,
    status_code=status.HTTP_200_OK,
    summary="RF04 — Actualizar parcialmente un estudiante",
    responses={
        404: {"description": "Estudiante no encontrado"},
        409: {"description": "Email o código ya registrado por otro estudiante"},
        422: {"description": "Datos inválidos"},
    },
)
def actualizar_estudiante(estudiante_id: int, datos: EstudianteUpdate, db: Session = Depends(get_db)):
    """Actualiza uno o más campos de un estudiante existente (PATCH parcial)."""
    estudiante = crud_est.obtener_estudiante_por_id(db, estudiante_id)
    if not estudiante:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estudiante no encontrado")

    # RF10: validar unicidad excluyendo al propio estudiante
    if datos.email and crud_est.existe_email(db, datos.email, excluir_id=estudiante_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El email ya está registrado por otro estudiante")
    if datos.codigo and crud_est.existe_codigo(db, datos.codigo, excluir_id=estudiante_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El código ya está registrado por otro estudiante")

    return crud_est.actualizar_estudiante(db, estudiante, datos)


@router.delete(
    "/{estudiante_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="RF05 — Eliminar un estudiante",
    responses={404: {"description": "Estudiante no encontrado"}},
)
def eliminar_estudiante(estudiante_id: int, db: Session = Depends(get_db)):
    """Elimina permanentemente un estudiante y todas sus inscripciones."""
    estudiante = crud_est.obtener_estudiante_por_id(db, estudiante_id)
    if not estudiante:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estudiante no encontrado")
    crud_est.eliminar_estudiante(db, estudiante)


@router.post(
    "/{estudiante_id}/materias/{materia_id}",
    status_code=status.HTTP_201_CREATED,
    summary="RF07 — Inscribir estudiante a una materia",
    responses={
        404: {"description": "Estudiante o materia no encontrados"},
        409: {"description": "El estudiante ya está inscrito en esta materia"},
    },
)
def inscribir_a_materia(estudiante_id: int, materia_id: int, db: Session = Depends(get_db)):
    """Inscribe a un estudiante en una materia. No se permiten inscripciones duplicadas."""
    if not crud_est.obtener_estudiante_por_id(db, estudiante_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estudiante no encontrado")
    if not crud_mat.obtener_materia_por_id(db, materia_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Materia no encontrada")

    # RF07: verificar duplicado
    if crud_mat.existe_inscripcion(db, estudiante_id, materia_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El estudiante ya está inscrito en esta materia")

    crud_mat.inscribir_estudiante(db, estudiante_id, materia_id)
    return {"mensaje": "Inscripción realizada exitosamente"}


@router.get(
    "/{estudiante_id}/materias",
    response_model=list[MateriaResponse],
    status_code=status.HTTP_200_OK,
    summary="RF08 — Listar materias de un estudiante",
    responses={404: {"description": "Estudiante no encontrado"}},
)
def listar_materias_de_estudiante(estudiante_id: int, db: Session = Depends(get_db)):
    """Retorna todas las materias en las que está inscrito el estudiante."""
    if not crud_est.obtener_estudiante_por_id(db, estudiante_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estudiante no encontrado")
    return crud_mat.obtener_materias_de_estudiante(db, estudiante_id)
