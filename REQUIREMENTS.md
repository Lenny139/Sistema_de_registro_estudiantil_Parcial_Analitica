# Sistema de Registro de Estudiantes
## Especificación de Requerimientos — v1.0

---

## 1. Descripción General

El Sistema de Registro de Estudiantes es una API RESTful que permite gestionar la información académica de los estudiantes de una institución educativa. El sistema centraliza el registro, consulta, actualización y eliminación de estudiantes, así como la administración de materias y la inscripción de estudiantes a las mismas. Está diseñado para ser consumido por aplicaciones frontend, sistemas administrativos o herramientas de integración institucional.

---

## 2. Requerimientos Funcionales

### RF01 — Registro de nuevo estudiante
El sistema debe permitir registrar un nuevo estudiante con los siguientes campos:
- `nombre` (obligatorio): nombre completo del estudiante.
- `id_estudiante` (obligatorio): identificador único institucional (código numérico o alfanumérico).
- `email` (obligatorio): correo electrónico único en el sistema.
- `carrera` (obligatorio): nombre del programa académico al que pertenece.
- `semestre` (obligatorio): semestre actual del estudiante (valor entero entre 1 y 12).
- `fecha_nacimiento` (obligatorio): fecha en formato ISO 8601 (YYYY-MM-DD).

### RF02 — Consulta de estudiante por ID
El sistema debe permitir buscar y retornar la información completa de un estudiante a partir de su `id_estudiante`. Si el estudiante no existe, debe retornar un error HTTP 404 con un mensaje descriptivo.

### RF03 — Consulta de estudiante por nombre
El sistema debe permitir buscar estudiantes por nombre o parte del nombre (búsqueda parcial, insensible a mayúsculas). Debe retornar una lista con todos los coincidentes. Si no hay resultados, retorna una lista vacía.

### RF04 — Actualización de datos de un estudiante
El sistema debe permitir actualizar uno o más campos de un estudiante existente identificado por su `id_estudiante`. Solo se actualizan los campos enviados en la solicitud (actualización parcial). El `id_estudiante` no puede ser modificado.

### RF05 — Eliminación de un estudiante
El sistema debe permitir eliminar de forma permanente el registro de un estudiante a partir de su `id_estudiante`. Si el estudiante no existe, retorna un error HTTP 404. La eliminación también debe remover las inscripciones asociadas a ese estudiante.

### RF06 — Listado completo de estudiantes
El sistema debe retornar la lista completa de todos los estudiantes registrados. Debe soportar paginación con parámetros `skip` (desplazamiento, por defecto 0) y `limit` (máximo de resultados, por defecto 10).

### RF07 — Creación de materias
El sistema debe permitir registrar materias con los siguientes campos:
- `codigo_materia` (obligatorio): código único de la materia (ej. MAT101).
- `nombre_materia` (obligatorio): nombre descriptivo de la materia.
- `creditos` (obligatorio): número de créditos académicos (entero entre 1 y 6).
- `docente` (obligatorio): nombre del docente responsable.

### RF08 — Inscripción de estudiante a una materia
El sistema debe permitir inscribir a un estudiante en una materia a partir de su `id_estudiante` y el `codigo_materia`. Si el estudiante ya está inscrito en esa materia, debe retornar un error HTTP 409 (conflicto). Si el estudiante o la materia no existen, retorna error HTTP 404.

### RF09 — Consulta de materias inscritas por estudiante
El sistema debe retornar la lista de todas las materias en las que está inscrito un estudiante, identificado por su `id_estudiante`. Si no tiene materias inscritas, retorna una lista vacía.

### RF10 — Validaciones de integridad de datos
El sistema debe aplicar las siguientes validaciones en todas las operaciones:
- El `email` debe tener formato válido y ser único en el sistema.
- El `id_estudiante` debe ser único en el sistema.
- El `codigo_materia` debe ser único en el sistema.
- El `semestre` debe ser un entero entre 1 y 12.
- Los `creditos` de una materia deben ser un entero entre 1 y 6.
- Los campos marcados como obligatorios no pueden ser nulos ni cadenas vacías.
- En caso de violación, el sistema retorna HTTP 422 con detalle del campo inválido.

---

## 3. Requerimientos No Funcionales

### RNF01 — Tiempo de respuesta
El sistema debe responder a cualquier solicitud en un tiempo máximo de 2 segundos bajo condiciones normales de operación (sin carga concurrente masiva).

### RNF02 — Persistencia de datos
Los datos deben persistir entre reinicios del servidor. Se utilizará SQLite como motor de base de datos embebido. La base de datos se almacenará en el archivo `./data/estudiantes.db`.

### RNF03 — Convenciones REST
Todos los endpoints deben seguir las convenciones REST:
- `GET` para consultas.
- `POST` para creación de recursos.
- `PUT` o `PATCH` para actualización.
- `DELETE` para eliminación.
- Los códigos HTTP deben ser semánticamente correctos (200, 201, 404, 409, 422, etc.).

### RNF04 — Cobertura de pruebas
El sistema debe contar con pruebas automatizadas que cubran al menos el 80% de los endpoints definidos. Las pruebas deben ejecutarse con `pytest` y utilizar una base de datos de prueba separada (`./data/test.db`) que se elimina al finalizar cada sesión de pruebas.

### RNF05 — Documentación automática
El sistema debe exponer documentación interactiva automática generada por FastAPI en las rutas `/docs` (Swagger UI) y `/redoc` (ReDoc).

### RNF06 — Estructura modular del código
El proyecto debe estar organizado en módulos separados por responsabilidad (modelos, esquemas, rutas, base de datos), facilitando el mantenimiento y la extensibilidad futura.

---

## 4. Stack Tecnológico

| Componente        | Tecnología         | Versión sugerida |
|-------------------|--------------------|------------------|
| Lenguaje          | Python             | 3.10+            |
| Framework API     | FastAPI            | 0.111+           |
| ORM               | SQLAlchemy         | 2.0+             |
| Base de datos     | SQLite             | (embebido)       |
| Validación        | Pydantic           | 2.0+             |
| Servidor ASGI     | Uvicorn            | 0.29+            |
| Pruebas           | Pytest + HTTPX     | latest           |

---

## 5. Estructura de Carpetas del Proyecto

```
student-registration-system/
│
├── main.py                  # Punto de entrada, instancia de FastAPI y registro de routers
├── database.py              # Configuración de SQLAlchemy y sesión de base de datos
├── models.py                # Modelos ORM (tablas de la base de datos)
├── schemas.py               # Esquemas Pydantic para validación de entrada/salida
├── requirements.txt         # Dependencias del proyecto
├── README.md                # Instrucciones de instalación y uso
│
├── routers/
│   ├── __init__.py
│   ├── students.py          # Endpoints relacionados con estudiantes (RF01–RF06, RF10)
│   └── courses.py           # Endpoints de materias e inscripciones (RF07–RF09)
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Configuración de pytest y fixtures de base de datos de prueba
│   ├── test_students.py     # Pruebas de endpoints de estudiantes
│   └── test_courses.py      # Pruebas de endpoints de materias e inscripciones
│
└── data/
    ├── estudiantes.db       # Base de datos de producción (generada automáticamente)
    └── test.db              # Base de datos de pruebas (generada y eliminada por pytest)
```

---

## 6. Endpoints del Sistema

### Estudiantes
| Método | Ruta                              | Descripción                        | RF        |
|--------|-----------------------------------|------------------------------------|-----------|
| POST   | `/students/`                      | Registrar nuevo estudiante         | RF01, RF10|
| GET    | `/students/`                      | Listar todos los estudiantes       | RF06      |
| GET    | `/students/{id_estudiante}`       | Consultar estudiante por ID        | RF02      |
| GET    | `/students/search/?nombre={...}`  | Buscar estudiante por nombre       | RF03      |
| PATCH  | `/students/{id_estudiante}`       | Actualizar datos del estudiante    | RF04, RF10|
| DELETE | `/students/{id_estudiante}`       | Eliminar estudiante                | RF05      |

### Materias e Inscripciones
| Método | Ruta                                          | Descripción                        | RF        |
|--------|-----------------------------------------------|------------------------------------|-----------|
| POST   | `/courses/`                                   | Crear nueva materia                | RF07, RF10|
| GET    | `/courses/`                                   | Listar todas las materias          | RF07      |
| POST   | `/courses/enroll/`                            | Inscribir estudiante en materia    | RF08      |
| GET    | `/students/{id_estudiante}/courses/`          | Consultar materias de un estudiante| RF09      |

---

## 7. Criterios de Aceptación

El sistema se considerará exitoso si:
1. Todos los endpoints responden correctamente con los códigos HTTP indicados.
2. Las validaciones de RF10 se aplican en cada operación de escritura.
3. Los datos persisten correctamente al reiniciar el servidor.
4. Las pruebas automatizadas se ejecutan sin errores con `pytest tests/ -v`.
5. La documentación Swagger es accesible en `http://localhost:8000/docs`.
