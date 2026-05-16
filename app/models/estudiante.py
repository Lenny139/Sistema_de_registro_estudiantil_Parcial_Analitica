"""Modelo ORM para la tabla de estudiantes.

Implementa: RF01 (campos del estudiante), RF10 (unicidad de email y código),
            RNF02 (persistencia), RNF03 (convenciones)
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Estudiante(Base):
    """Representa un estudiante registrado en el sistema."""

    __tablename__ = "estudiantes"

    # RF01: Campos obligatorios del estudiante
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(150), nullable=False, index=True)
    codigo = Column(String(20), nullable=False, unique=True, index=True)   # RF10: código único
    email = Column(String(150), nullable=False, unique=True, index=True)   # RF10: email único
    carrera = Column(String(100), nullable=False)
    semestre = Column(Integer, nullable=False)                              # RF10: rango 1-12 validado en schema

    # RF07, RF08: Relación N:M con materias a través de inscripciones
    inscripciones = relationship(
        "Inscripcion",
        back_populates="estudiante",
        cascade="all, delete-orphan",   # RF05: eliminar inscripciones al borrar estudiante
        lazy="select",
    )
