# REQUIREMENTS.md
# Sistema de Registro de Estudiantes
**Versión:** 1.0.0
**Fecha:** 2026-05-16
**Marco de desarrollo:** SDD (Specification Driven Development)

---

## 1. Descripción General del Sistema

El **Sistema de Registro de Estudiantes** es una aplicación backend de tipo REST API diseñada para gestionar la información académica de los estudiantes de una institución educativa. Permite registrar, consultar, actualizar y eliminar estudiantes, así como administrar su inscripción a materias.

El sistema actúa como fuente centralizada de verdad para los datos estudiantiles, garantizando integridad referencial, unicidad de identificadores y trazabilidad de la información académica.

**Alcance:**
- Gestión completa del ciclo de vida de un estudiante en el sistema.
- Administración de materias disponibles.
- Relación muchos-a-muchos entre estudiantes y materias (inscripciones).
- Exposición de una API RESTful consumible por cualquier cliente (web, móvil, herramientas de análisis).

---

## 2. Requerimientos Funcionales

### RF01 — Registro de Nuevos Estudiantes
El sistema debe permitir crear un nuevo registro de estudiante con los siguientes campos:

| Campo      | Tipo    | Obligatorio | Descripción                        |
|------------|---------|-------------|------------------------------------|
| `id`       | Integer | Sí (auto)   | Identificador único autoincremental |
| `nombre`   | String  | Sí          | Nombre completo del estudiante     |
| `codigo`   | String  | Sí          | Código estudiantil único           |
| `email`    | String  | Sí          | Correo electrónico único           |
| `carrera`  | String  | Sí          | Nombre del programa académico      |
| `semestre` | Integer | Sí          | Semestre actual (1–12)             |

**Criterio de aceptación:** El endpoint `POST /estudiantes` retorna `201 Created` con el objeto creado; retorna `422 Unprocessable Entity` si faltan campos obligatorios o los datos son inválidos.

---

### RF02 — Consulta de Estudiante por ID
El sistema debe permitir obtener los datos completos de un estudiante a partir de su identificador único interno.

**Criterio de aceptación:** `GET /estudiantes/{id}` retorna `200 OK` con el objeto del estudiante; retorna `404 Not Found` si el ID no existe.

---

### RF03 — Consulta de Estudiantes por Nombre
El sistema debe permitir buscar estudiantes cuyo nombre contenga una cadena de texto (búsqueda parcial, sin distinción de mayúsculas/minúsculas).

**Criterio de aceptación:** `GET /estudiantes?nombre={texto}` retorna `200 OK` con una lista (vacía si no hay coincidencias).

---

### RF04 — Actualización de Datos de un Estudiante
El sistema debe permitir modificar uno o más campos de un estudiante existente. Solo se actualizan los campos incluidos en el cuerpo de la solicitud (actualización parcial).

**Criterio de aceptación:** `PATCH /estudiantes/{id}` retorna `200 OK` con el objeto actualizado; retorna `404 Not Found` si el ID no existe; retorna `422` si los nuevos datos violan validaciones.

---

### RF05 — Eliminación de un Estudiante
El sistema debe permitir eliminar permanentemente el registro de un estudiante. La eliminación debe remover también sus inscripciones activas.

**Criterio de aceptación:** `DELETE /estudiantes/{id}` retorna `204 No Content`; retorna `404 Not Found` si el ID no existe.

---

### RF06 — Listado Completo de Estudiantes
El sistema debe exponer un endpoint que retorne la lista de todos los estudiantes registrados, con soporte para paginación opcional.

**Criterio de aceptación:** `GET /estudiantes` retorna `200 OK` con una lista de objetos. Parámetros opcionales: `skip` (offset) y `limit` (máximo de resultados, default 100).

---

### RF07 — Inscripción de Estudiantes a Materias
El sistema debe permitir inscribir a un estudiante en una materia existente. Un estudiante no puede inscribirse dos veces en la misma materia.

**Criterio de aceptación:** `POST /estudiantes/{id}/materias/{materia_id}` retorna `201 Created`; retorna `409 Conflict` si la inscripción ya existe; retorna `404 Not Found` si el estudiante o la materia no existen.

---

### RF08 — Consulta de Materias por Estudiante
El sistema debe permitir obtener la lista de todas las materias en las que está inscrito un estudiante.

**Criterio de aceptación:** `GET /estudiantes/{id}/materias` retorna `200 OK` con la lista de materias; retorna `404 Not Found` si el estudiante no existe.

---

### RF09 — Gestión de Materias
El sistema debe permitir crear, listar y eliminar materias disponibles en la institución.

| Campo        | Tipo    | Obligatorio | Descripción                  |
|--------------|---------|-------------|------------------------------|
| `id`         | Integer | Sí (auto)   | Identificador único           |
| `nombre`     | String  | Sí          | Nombre de la materia          |
| `codigo`     | String  | Sí          | Código único de la materia    |
| `creditos`   | Integer | Sí          | Número de créditos (1–10)    |

**Criterio de aceptación:** `POST /materias` retorna `201 Created`; `GET /materias` retorna la lista completa; `DELETE /materias/{id}` retorna `204 No Content`.

---

### RF10 — Validaciones de Datos
El sistema debe garantizar las siguientes restricciones de integridad:

- **Email único:** No pueden existir dos estudiantes con el mismo email. Retorna `409 Conflict`.
- **Código único:** El campo `codigo` de estudiante debe ser único. Retorna `409 Conflict`.
- **Campos obligatorios:** Todos los campos marcados como obligatorios deben estar presentes. Retorna `422 Unprocessable Entity`.
- **Semestre válido:** El semestre debe ser un entero entre 1 y 12 inclusive.
- **Email con formato válido:** Debe seguir el patrón estándar de correo electrónico.
- **Créditos válidos:** El número de créditos de una materia debe estar entre 1 y 10.

---

## 3. Requerimientos No Funcionales

### RNF01 — Tiempo de Respuesta
Todos los endpoints deben responder en menos de **500 ms** bajo carga normal (hasta 50 solicitudes concurrentes) en un entorno de desarrollo local. Las operaciones de consulta simple deben completarse en menos de **100 ms**.

---

### RNF02 — Persistencia de Datos
Los datos deben ser persistidos en una base de datos relacional (**SQLite**) mediante un archivo local (`estudiantes.db`). La base de datos debe:
- Sobrevivir reinicios del servidor.
- Ser inicializada automáticamente al arrancar la aplicación (creación de tablas si no existen).
- Mantener integridad referencial mediante claves foráneas.

---

### RNF03 — Convenciones de Código
El código fuente debe adherirse a los siguientes estándares:
- **PEP 8** para estilo de código Python.
- **Snake_case** para variables, funciones y nombres de archivo.
- **PascalCase** para clases y modelos Pydantic.
- Separación clara en capas: `models` (ORM), `schemas` (Pydantic), `routers` (endpoints), `crud` (lógica de datos).
- Todos los módulos públicos deben tener docstrings descriptivos.

---

### RNF04 — Cobertura de Pruebas
El proyecto debe incluir una suite de pruebas automatizadas con las siguientes características:
- Cobertura mínima del **80%** del código de negocio.
- Pruebas unitarias para funciones de validación y lógica CRUD.
- Pruebas de integración para cada endpoint (usando `TestClient` de FastAPI).
- Base de datos en memoria (`SQLite :memory:`) para pruebas, aislada de producción.
- Ejecutables con `pytest` desde la raíz del proyecto.

---

### RNF05 — Documentación Automática
La API debe exponer documentación interactiva automática mediante:
- **Swagger UI** en `/docs`
- **ReDoc** en `/redoc`

Cada endpoint debe tener descripción, ejemplos de request/response y códigos de estado documentados.

---

## 4. Stack Tecnológico

| Componente         | Tecnología              | Versión sugerida | Justificación                                      |
|--------------------|-------------------------|------------------|----------------------------------------------------|
| Lenguaje           | Python                  | 3.11+            | Ecosistema maduro, tipado estático opcional        |
| Framework web      | FastAPI                 | 0.111+           | Alto rendimiento, documentación automática, tipado |
| ORM                | SQLAlchemy              | 2.0+             | Abstracción robusta sobre SQL, soporte SQLite      |
| Base de datos      | SQLite                  | Built-in         | Sin instalación externa, ideal para desarrollo     |
| Validación         | Pydantic                | 2.0+             | Validación declarativa integrada con FastAPI       |
| Servidor ASGI      | Uvicorn                 | 0.29+            | Servidor liviano y eficiente para FastAPI          |
| Testing            | Pytest + httpx          | Latest           | Framework estándar de testing en Python            |
| Cobertura          | pytest-cov              | Latest           | Reporte de cobertura integrado con pytest          |

---

## 5. Estructura de Carpetas Propuesta

```
Sistema_de_registro_estudiantil_Parcial_Analitica/
│
├── REQUIREMENTS.md               # Este archivo — fuente de verdad del proyecto
├── README.md                     # Instrucciones de instalación y uso
├── requirements.txt              # Dependencias del proyecto
│
├── app/
│   ├── __init__.py
│   ├── main.py                   # Punto de entrada: instancia FastAPI, registra routers
│   ├── database.py               # Configuración de conexión SQLAlchemy y sesión
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── estudiante.py         # Modelo ORM: tabla `estudiantes`
│   │   ├── materia.py            # Modelo ORM: tabla `materias`
│   │   └── inscripcion.py        # Modelo ORM: tabla `inscripciones` (relación N:M)
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── estudiante.py         # Schemas Pydantic: request/response de estudiantes
│   │   └── materia.py            # Schemas Pydantic: request/response de materias
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── estudiantes.py        # Endpoints: /estudiantes y /estudiantes/{id}
│   │   └── materias.py           # Endpoints: /materias y /estudiantes/{id}/materias
│   │
│   └── crud/
│       ├── __init__.py
│       ├── estudiante.py         # Funciones CRUD para estudiantes
│       └── materia.py            # Funciones CRUD para materias e inscripciones
│
└── tests/
    ├── __init__.py
    ├── conftest.py               # Fixtures compartidos: cliente de prueba, BD en memoria
    ├── test_estudiantes.py       # Pruebas de integración: endpoints de estudiantes
    ├── test_materias.py          # Pruebas de integración: endpoints de materias
    └── test_inscripciones.py     # Pruebas de integración: inscripciones
```

---

## 6. Convenciones de la API REST

| Operación                        | Método   | Endpoint                                  | Código éxito |
|----------------------------------|----------|-------------------------------------------|--------------|
| Crear estudiante                 | `POST`   | `/estudiantes`                            | `201`        |
| Listar estudiantes               | `GET`    | `/estudiantes`                            | `200`        |
| Obtener estudiante por ID        | `GET`    | `/estudiantes/{id}`                       | `200`        |
| Actualizar estudiante            | `PATCH`  | `/estudiantes/{id}`                       | `200`        |
| Eliminar estudiante              | `DELETE` | `/estudiantes/{id}`                       | `204`        |
| Crear materia                    | `POST`   | `/materias`                               | `201`        |
| Listar materias                  | `GET`    | `/materias`                               | `200`        |
| Eliminar materia                 | `DELETE` | `/materias/{id}`                          | `204`        |
| Inscribir estudiante a materia   | `POST`   | `/estudiantes/{id}/materias/{materia_id}` | `201`        |
| Listar materias de un estudiante | `GET`    | `/estudiantes/{id}/materias`              | `200`        |

---

*Este documento es la fuente de verdad del proyecto. Cualquier cambio en los requerimientos debe ser reflejado aquí antes de modificar el código.*
