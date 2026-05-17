"""Integration tests for student endpoints.

Covers: RF01 (create), RF02 (get by ID), RF03 (search by name),
        RF04 (update), RF05 (delete), RF06 (list/pagination), RF10 (validations)
"""

BASE = {
    "nombre": "Test User",
    "codigo": "STU-001",
    "email": "test@uni.edu",
    "carrera": "Ingeniería de Sistemas",
    "semestre": 3,
}


def _create(client, overrides=None):
    """Helper: creates a student and returns the response."""
    data = {**BASE, **(overrides or {})}
    return client.post("/estudiantes/", json=data)


# ── RF01: Create student ────────────────────────────────────────────────────

def test_create_student_success(client):
    """RF01: POST /estudiantes/ with valid data returns 201 and the created object."""
    resp = _create(client)
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == BASE["email"]
    assert body["codigo"] == BASE["codigo"]
    assert isinstance(body["id"], int)


# ── RF10: Uniqueness validations ────────────────────────────────────────────

def test_create_duplicate_email(client):
    """RF10: Registering a student with an already-used email returns 409."""
    _create(client)
    resp = _create(client, {"codigo": "STU-002"})  # same email, different code
    assert resp.status_code == 409
    assert "email" in resp.json()["detail"].lower()


def test_create_duplicate_codigo(client):
    """RF10: Registering a student with an already-used codigo returns 409."""
    _create(client)
    resp = _create(client, {"email": "other@uni.edu"})  # same code, different email
    assert resp.status_code == 409
    assert "código" in resp.json()["detail"].lower()


def test_create_missing_required_fields(client):
    """RF10: Missing required field (nombre empty string) returns 422."""
    resp = _create(client, {"nombre": ""})
    assert resp.status_code == 422


def test_create_invalid_semestre(client):
    """RF10: semestre outside 1-12 returns 422."""
    resp = _create(client, {"semestre": 13})
    assert resp.status_code == 422


def test_create_invalid_email_format(client):
    """RF10: Malformed email returns 422."""
    resp = _create(client, {"email": "not-an-email"})
    assert resp.status_code == 422


# ── RF02: Get student by ID ─────────────────────────────────────────────────

def test_get_student_by_id_exists(client):
    """RF02: GET /estudiantes/{id} for an existing student returns 200."""
    student_id = _create(client).json()["id"]
    resp = client.get(f"/estudiantes/{student_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == student_id


def test_get_student_by_id_not_found(client):
    """RF02: GET /estudiantes/{id} for a non-existent ID returns 404."""
    resp = client.get("/estudiantes/9999")
    assert resp.status_code == 404


# ── RF03: Search by name ────────────────────────────────────────────────────

def test_search_by_full_name(client):
    """RF03: Searching by full name returns the matching student."""
    _create(client)
    resp = client.get("/estudiantes/", params={"nombre": "Test User"})
    assert resp.status_code == 200
    assert len(resp.json()) >= 1
    assert resp.json()[0]["nombre"] == "Test User"


def test_search_by_partial_name(client):
    """RF03: Partial name search (case-insensitive) returns matches."""
    _create(client)
    resp = client.get("/estudiantes/", params={"nombre": "test"})
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_search_no_match_returns_empty_list(client):
    """RF03: Search with no match returns an empty list, not 404."""
    _create(client)
    resp = client.get("/estudiantes/", params={"nombre": "zzznomatch"})
    assert resp.status_code == 200
    assert resp.json() == []


# ── RF04: Update student ────────────────────────────────────────────────────

def test_update_existing_student(client):
    """RF04: PATCH /estudiantes/{id} updates only the supplied fields."""
    student_id = _create(client).json()["id"]
    resp = client.patch(f"/estudiantes/{student_id}", json={"semestre": 8})
    assert resp.status_code == 200
    assert resp.json()["semestre"] == 8
    # Other fields unchanged
    assert resp.json()["nombre"] == BASE["nombre"]


def test_update_nonexistent_student(client):
    """RF04: PATCH on a non-existent ID returns 404."""
    resp = client.patch("/estudiantes/9999", json={"semestre": 5})
    assert resp.status_code == 404


# ── RF05: Delete student ────────────────────────────────────────────────────

def test_delete_existing_student(client):
    """RF05: DELETE /estudiantes/{id} returns 204 and the record is gone."""
    student_id = _create(client).json()["id"]
    resp = client.delete(f"/estudiantes/{student_id}")
    assert resp.status_code == 204
    assert client.get(f"/estudiantes/{student_id}").status_code == 404


def test_delete_nonexistent_student(client):
    """RF05: DELETE on a non-existent ID returns 404."""
    resp = client.delete("/estudiantes/9999")
    assert resp.status_code == 404


# ── RF06: List students + pagination ───────────────────────────────────────

def test_list_all_students(client):
    """RF06: GET /estudiantes/ returns 200 with all registered students."""
    _create(client)
    _create(client, {"codigo": "STU-002", "email": "b@uni.edu"})
    resp = client.get("/estudiantes/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_pagination_skip_limit(client):
    """RF06: skip and limit parameters correctly paginate results."""
    for i in range(3):
        _create(client, {"codigo": f"STU-{i:03d}", "email": f"user{i}@uni.edu"})
    resp = client.get("/estudiantes/", params={"skip": 1, "limit": 1})
    assert resp.status_code == 200
    assert len(resp.json()) == 1
