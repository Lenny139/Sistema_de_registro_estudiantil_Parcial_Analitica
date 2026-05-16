"""Modelo ORM para la tabla de inscripciones (relación N:M entre estudiantes y materias).

Implementa: RF07 (inscripción a materias), RF08 (consulta de materias por estudiante),
            RF05 (eliminación en cascada), RNF02 (integridad referencial)
"""

from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Inscripcion(Base):
    """Tabla de asociación entre estudiantes y materias."""

    __tablename__ = "inscripciones"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # RNF02: Claves foráneas con integridad referencial
    estudiante_id = Column(Integer, ForeignKey("estudiantes.id", ondelete="CASCADE"), nullable=False)
    materia_id = Column(Integer, ForeignKey("materias.id", ondelete="CASCADE"), nullable=False)

    # RF07: Un estudiante no puede inscribirse dos veces a la misma materia
    __table_args__ = (
        UniqueConstraint("estudiante_id", "materia_id", name="uq_estudiante_materia"),
    )

    estudiante = relationship("Estudiante", back_populates="inscripciones")
    materia = relationship("Materia", back_populates="inscripciones")
