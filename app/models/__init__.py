# RNF03: Exporta todos los modelos ORM para que SQLAlchemy los registre al crear tablas
from app.models.estudiante import Estudiante
from app.models.materia import Materia
from app.models.inscripcion import Inscripcion

__all__ = ["Estudiante", "Materia", "Inscripcion"]
