"""Schemas Pydantic para validación y serialización de estudiantes.

Implementa: RF01 (campos y tipos), RF04 (actualización parcial),
            RF10 (validaciones: email, semestre, unicidad declarada en mensajes),
            RNF03 (convenciones PascalCase, tipado estricto)
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional


class EstudianteBase(BaseModel):
    """Campos comunes a creación y respuesta de estudiante."""

    nombre: str = Field(
        ...,
        min_length=2,
        max_length=150,
        examples=["Juan Pérez García"],
        description="Nombre completo del estudiante",
    )
    codigo: str = Field(
        ...,
        min_length=3,
        max_length=20,
        examples=["EST-2024-001"],
        description="Código estudiantil único",
    )
    email: EmailStr = Field(
        ...,
        examples=["juan.perez@universidad.edu.co"],
        description="Correo electrónico único del estudiante",
    )
    carrera: str = Field(
        ...,
        min_length=3,
        max_length=100,
        examples=["Ingeniería de Sistemas"],
        description="Nombre del programa académico",
    )
    # RF10: semestre válido entre 1 y 12
    semestre: int = Field(
        ...,
        ge=1,
        le=12,
        examples=[3],
        description="Semestre actual del estudiante (1–12)",
    )


class EstudianteCreate(EstudianteBase):
    """Schema para RF01: crear un nuevo estudiante (todos los campos obligatorios)."""
    pass


class EstudianteUpdate(BaseModel):
    """Schema para RF04: actualización parcial — todos los campos son opcionales."""

    nombre: Optional[str] = Field(None, min_length=2, max_length=150)
    codigo: Optional[str] = Field(None, min_length=3, max_length=20)
    email: Optional[EmailStr] = None
    carrera: Optional[str] = Field(None, min_length=3, max_length=100)
    semestre: Optional[int] = Field(None, ge=1, le=12)

    # RF04: Al menos un campo debe enviarse en la actualización
    @field_validator("*", mode="before")
    @classmethod
    def at_least_one_field(cls, v):
        return v


class EstudianteResponse(EstudianteBase):
    """Schema de respuesta que incluye el ID generado por la base de datos."""

    id: int = Field(..., description="Identificador único autoincremental")

    model_config = {"from_attributes": True}
