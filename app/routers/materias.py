"""Endpoints REST para la gestión de materias.

Implementa: RF09 (POST /materias, GET /materias, DELETE /materias/{id}),
            RF10 (código único de materia), RNF05 (documentación Swagger)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.materia import MateriaCreate, MateriaResponse
from app.crud import materia as crud_mat

router = APIRouter(prefix="/materias", tags=["Materias"])


@router.post(
    "/",
    response_model=MateriaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="RF09 — Crear nueva materia",
    responses={
        409: {"description": "Código de materia ya registrado"},
        422: {"description": "Datos inválidos o campos faltantes"},
    },
)
def crear_materia(datos: MateriaCreate, db: Session = Depends(get_db)):
    """Registra una nueva materia. El código debe ser único."""
    # RF10: validar código único
    if crud_mat.existe_codigo_materia(db, datos.codigo):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El código de materia ya está registrado")
    return crud_mat.crear_materia(db, datos)


@router.get(
    "/",
    response_model=list[MateriaResponse],
    status_code=status.HTTP_200_OK,
    summary="RF09 — Listar todas las materias",
)
def listar_materias(
    skip: int = Query(0, ge=0, description="Registros a omitir"),
    limit: int = Query(100, ge=1, le=500, description="Máximo de registros"),
    db: Session = Depends(get_db),
):
    """Retorna el listado completo de materias disponibles."""
    return crud_mat.obtener_materias(db, skip=skip, limit=limit)


@router.get(
    "/{materia_id}",
    response_model=MateriaResponse,
    status_code=status.HTTP_200_OK,
    summary="RF09 — Obtener materia por ID",
    responses={404: {"description": "Materia no encontrada"}},
)
def obtener_materia(materia_id: int, db: Session = Depends(get_db)):
    """Retorna los datos de una materia específica."""
    materia = crud_mat.obtener_materia_por_id(db, materia_id)
    if not materia:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Materia no encontrada")
    return materia


@router.delete(
    "/{materia_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="RF09 — Eliminar una materia",
    responses={404: {"description": "Materia no encontrada"}},
)
def eliminar_materia(materia_id: int, db: Session = Depends(get_db)):
    """Elimina permanentemente una materia y sus inscripciones asociadas."""
    materia = crud_mat.obtener_materia_por_id(db, materia_id)
    if not materia:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Materia no encontrada")
    crud_mat.eliminar_materia(db, materia)
