# Sistema de Registro de Estudiantes

API RESTful para gestión académica de estudiantes, materias e inscripciones.
Desarrollado con **Python + FastAPI + SQLite** bajo el marco SDD.

---

## Requisitos

- Python 3.11 o superior
- pip

---

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/Lenny139/Sistema_de_registro_estudiantil_Parcial_Analitica.git
cd Sistema_de_registro_estudiantil_Parcial_Analitica

# 2. Crear entorno virtual
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt
```

---

## Ejecutar la aplicación

```bash
uvicorn app.main:app --reload
```

La API quedará disponible en: `http://127.0.0.1:8000`

| Recurso            | URL                          |
|--------------------|------------------------------|
| Swagger UI         | http://127.0.0.1:8000/docs   |
| ReDoc              | http://127.0.0.1:8000/redoc  |
| Health check       | http://127.0.0.1:8000/       |

La base de datos `estudiantes.db` se crea automáticamente en la raíz del proyecto al primer inicio.

---

## Endpoints disponibles

### Estudiantes

| Método   | Endpoint                                    | Descripción                        |
|----------|---------------------------------------------|------------------------------------|
| `POST`   | `/estudiantes/`                             | Registrar nuevo estudiante         |
| `GET`    | `/estudiantes/`                             | Listar todos (con paginación)      |
| `GET`    | `/estudiantes/?nombre={texto}`              | Buscar por nombre (parcial)        |
| `GET`    | `/estudiantes/{id}`                         | Obtener estudiante por ID          |
| `PATCH`  | `/estudiantes/{id}`                         | Actualizar parcialmente            |
| `DELETE` | `/estudiantes/{id}`                         | Eliminar estudiante                |
| `POST`   | `/estudiantes/{id}/materias/{materia_id}`   | Inscribir a materia                |
| `GET`    | `/estudiantes/{id}/materias`                | Ver materias inscritas             |

### Materias

| Método   | Endpoint           | Descripción              |
|----------|--------------------|--------------------------|
| `POST`   | `/materias/`       | Crear nueva materia      |
| `GET`    | `/materias/`       | Listar todas las materias|
| `GET`    | `/materias/{id}`   | Obtener materia por ID   |
| `DELETE` | `/materias/{id}`   | Eliminar materia         |

---

## Ejemplo de uso rápido

```bash
# Crear un estudiante
curl -X POST http://127.0.0.1:8000/estudiantes/ \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Ana Torres","codigo":"EST-001","email":"ana@uni.edu","carrera":"Ingeniería de Sistemas","semestre":3}'

# Crear una materia
curl -X POST http://127.0.0.1:8000/materias/ \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Cálculo Diferencial","codigo":"MAT-101","creditos":4}'

# Inscribir al estudiante en la materia (reemplazar IDs)
curl -X POST http://127.0.0.1:8000/estudiantes/1/materias/1
```

---

## Ejecutar pruebas

```bash
# Todas las pruebas
pytest

# Con reporte de cobertura
pytest --cov=app --cov-report=term-missing

# Verbose
pytest -v
```

Cobertura objetivo: **≥ 80%** (RNF04).

---

## Estructura del proyecto

```
├── REQUIREMENTS.md          # Fuente de verdad del proyecto (SDD)
├── README.md
├── requirements.txt
├── app/
│   ├── main.py              # Punto de entrada FastAPI
│   ├── database.py          # Configuración SQLite + SQLAlchemy
│   ├── models/
│   │   ├── estudiante.py    # Tabla estudiantes
│   │   ├── materia.py       # Tabla materias
│   │   └── inscripcion.py   # Tabla inscripciones (N:M)
│   ├── schemas/
│   │   ├── estudiante.py    # Validación Pydantic estudiantes
│   │   └── materia.py       # Validación Pydantic materias
│   ├── routers/
│   │   ├── estudiantes.py   # Endpoints /estudiantes
│   │   └── materias.py      # Endpoints /materias
│   └── crud/
│       ├── estudiante.py    # Lógica de datos estudiantes
│       └── materia.py       # Lógica de datos materias e inscripciones
└── tests/
    ├── conftest.py          # Fixtures (BD en memoria)
    ├── test_estudiantes.py
    ├── test_materias.py
    └── test_inscripciones.py
```

---

## Validaciones implementadas (RF10)

| Regla                   | Comportamiento        |
|-------------------------|-----------------------|
| Email duplicado         | `409 Conflict`        |
| Código duplicado        | `409 Conflict`        |
| Campo obligatorio vacío | `422 Unprocessable`   |
| Semestre fuera de 1–12  | `422 Unprocessable`   |
| Email con formato inválido | `422 Unprocessable` |
| Créditos fuera de 1–10  | `422 Unprocessable`   |
| Inscripción duplicada   | `409 Conflict`        |
