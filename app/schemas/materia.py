"""Schemas Pydantic para validación y serialización de materias.

Implementa: RF09 (campos de materia), RF10 (créditos válidos 1-10),
            RNF03 (convenciones, tipado estricto)
"""

from pydantic import BaseModel, Field


class MateriaBase(BaseModel):
    """Campos comunes a creación y respuesta de materia."""

    nombre: str = Field(
        ...,
        min_length=2,
        max_length=150,
        examples=["Cálculo Diferencial"],
        description="Nombre de la materia",
    )
    codigo: str = Field(
        ...,
        min_length=2,
        max_length=20,
        examples=["MAT-101"],
        description="Código único de la materia",
    )
    # RF10: créditos válidos entre 1 y 10
    creditos: int = Field(
        ...,
        ge=1,
        le=10,
        examples=[4],
        description="Número de créditos académicos (1–10)",
    )


class MateriaCreate(MateriaBase):
    """Schema para RF09: crear una nueva materia (todos los campos obligatorios)."""
    pass


class MateriaResponse(MateriaBase):
    """Schema de respuesta que incluye el ID generado por la base de datos."""

    id: int = Field(..., description="Identificador único autoincremental")

    model_config = {"from_attributes": True}
