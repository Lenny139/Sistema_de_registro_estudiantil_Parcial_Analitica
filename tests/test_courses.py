"""Integration tests for courses and enrollment endpoints.

Covers: RF07 (enroll), RF08 (get enrolled courses), RF09 (course CRUD), RF10 (validations)
"""

COURSE = {
    "nombre": "Algebra Lineal",
    "codigo": "MAT-001",
    "creditos": 4,
}

STUDENT = {
    "nombre": "Juan Garcia",
    "codigo": "EST-001",
    "email": "juan@uni.edu",
    "carrera": "Fisica",
    "semestre": 1,
}


def _create_course(client, overrides=None):
    return client.post("/materias/", json={**COURSE, **(overrides or {})})


def _create_student(client, overrides=None):
    return client.post("/estudiantes/", json={**STUDENT, **(overrides or {})})


# ── RF09: Create and list courses ───────────────────────────────────────────

def test_create_course_success(client):
    """RF09: POST /materias/ with valid data returns 201."""
    resp = _create_course(client)
    assert resp.status_code == 201
    body = resp.json()
    assert body["codigo"] == COURSE["codigo"]
    assert isinstance(body["id"], int)


def test_create_duplicate_course_code(client):
    """RF10: Creating a course with a duplicate codigo returns 409."""
    _create_course(client)
    resp = _create_course(client, {"nombre": "Otro nombre"})  # same codigo
    assert resp.status_code == 409


def test_create_course_invalid_credits(client):
    """RF10: creditos outside 1-10 returns 422."""
    resp = _create_course(client, {"creditos": 0})
    assert resp.status_code == 422


def test_list_all_courses(client):
    """RF09: GET /materias/ returns 200 with all courses."""
    _create_course(client)
    _create_course(client, {"codigo": "MAT-002", "nombre": "Calculo"})
    resp = client.get("/materias/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


# ── RF07: Enroll student in course ─────────────────────────────────────────

def test_enroll_student_success(client):
    """RF07: POST /estudiantes/{id}/materias/{mid} returns 201."""
    est_id = _create_student(client).json()["id"]
    mat_id = _create_course(client).json()["id"]
    resp = client.post(f"/estudiantes/{est_id}/materias/{mat_id}")
    assert resp.status_code == 201
    assert "exitosamente" in resp.json()["mensaje"].lower()


def test_enroll_duplicate(client):
    """RF07: Enrolling the same student in the same course twice returns 409."""
    est_id = _create_student(client).json()["id"]
    mat_id = _create_course(client).json()["id"]
    client.post(f"/estudiantes/{est_id}/materias/{mat_id}")
    resp = client.post(f"/estudiantes/{est_id}/materias/{mat_id}")
    assert resp.status_code == 409


def test_enroll_nonexistent_student(client):
    """RF07: Enrolling a non-existent student returns 404."""
    mat_id = _create_course(client).json()["id"]
    resp = client.post(f"/estudiantes/9999/materias/{mat_id}")
    assert resp.status_code == 404


def test_enroll_nonexistent_course(client):
    """RF07: Enrolling in a non-existent course returns 404."""
    est_id = _create_student(client).json()["id"]
    resp = client.post(f"/estudiantes/{est_id}/materias/9999")
    assert resp.status_code == 404


# ── RF08: Get courses for a student ────────────────────────────────────────

def test_get_student_courses(client):
    """RF08: GET /estudiantes/{id}/materias returns enrolled courses."""
    est_id = _create_student(client).json()["id"]
    mat_id = _create_course(client).json()["id"]
    client.post(f"/estudiantes/{est_id}/materias/{mat_id}")
    resp = client.get(f"/estudiantes/{est_id}/materias")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["id"] == mat_id


def test_get_student_courses_empty(client):
    """RF08: Student with no enrollments returns an empty list, not 404."""
    est_id = _create_student(client).json()["id"]
    resp = client.get(f"/estudiantes/{est_id}/materias")
    assert resp.status_code == 200
    assert resp.json() == []
