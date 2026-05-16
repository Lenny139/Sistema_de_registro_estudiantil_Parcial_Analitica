"""Modelo ORM para la tabla de materias.

Implementa: RF09 (gestión de materias), RF10 (código único, créditos válidos),
            RNF02 (persistencia), RNF03 (convenciones)
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Materia(Base):
    """Representa una materia disponible en la institución."""

    __tablename__ = "materias"

    # RF09: Campos obligatorios de la materia
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(150), nullable=False)
    codigo = Column(String(20), nullable=False, unique=True, index=True)   # RF10: código único
    creditos = Column(Integer, nullable=False)                             # RF10: rango 1-10 validado en schema

    # RF07: Relación N:M con estudiantes
    inscripciones = relationship(
        "Inscripcion",
        back_populates="materia",
        cascade="all, delete-orphan",
        lazy="select",
    )
