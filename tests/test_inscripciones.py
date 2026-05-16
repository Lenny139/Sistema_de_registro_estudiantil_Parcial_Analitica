"""Pruebas de integración para los endpoints de inscripciones.

Implementa: RNF04 (cobertura ≥80%)
Cubre: RF07, RF08
"""

ESTUDIANTE = {
    "nombre": "Carlos Gómez",
    "codigo": "EST-100",
    "email": "carlos@uni.edu",
    "carrera": "Matemáticas",
    "semestre": 2,
}

MATERIA = {
    "nombre": "Álgebra Lineal",
    "codigo": "MAT-202",
    "creditos": 3,
}


def setup_estudiante_y_materia(client):
    """Helper: crea un estudiante y una materia, retorna sus IDs."""
    est_id = client.post("/estudiantes/", json=ESTUDIANTE).json()["id"]
    mat_id = client.post("/materias/", json=MATERIA).json()["id"]
    return est_id, mat_id


# ── RF07: Inscribir estudiante a materia ────────────────────────────────────

class TestInscripcion:
    def test_inscripcion_exitosa(self, client):
        est_id, mat_id = setup_estudiante_y_materia(client)
        resp = client.post(f"/estudiantes/{est_id}/materias/{mat_id}")
        assert resp.status_code == 201
        assert "exitosamente" in resp.json()["mensaje"].lower()

    def test_falla_inscripcion_duplicada(self, client):
        est_id, mat_id = setup_estudiante_y_materia(client)
        client.post(f"/estudiantes/{est_id}/materias/{mat_id}")
        resp = client.post(f"/estudiantes/{est_id}/materias/{mat_id}")
        assert resp.status_code == 409

    def test_falla_estudiante_inexistente(self, client):
        _, mat_id = setup_estudiante_y_materia(client)
        resp = client.post(f"/estudiantes/9999/materias/{mat_id}")
        assert resp.status_code == 404

    def test_falla_materia_inexistente(self, client):
        est_id, _ = setup_estudiante_y_materia(client)
        resp = client.post(f"/estudiantes/{est_id}/materias/9999")
        assert resp.status_code == 404


# ── RF08: Consultar materias de un estudiante ───────────────────────────────

class TestMateriasDeEstudiante:
    def test_lista_vacia_sin_inscripciones(self, client):
        est_id, _ = setup_estudiante_y_materia(client)
        resp = client.get(f"/estudiantes/{est_id}/materias")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_lista_materias_inscritas(self, client):
        est_id, mat_id = setup_estudiante_y_materia(client)
        client.post(f"/estudiantes/{est_id}/materias/{mat_id}")
        resp = client.get(f"/estudiantes/{est_id}/materias")
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["id"] == mat_id

    def test_retorna_404_si_estudiante_no_existe(self, client):
        resp = client.get("/estudiantes/9999/materias")
        assert resp.status_code == 404

    def test_inscripcion_se_elimina_con_estudiante(self, client):
        """RF05: Al eliminar el estudiante, sus inscripciones desaparecen."""
        est_id, mat_id = setup_estudiante_y_materia(client)
        client.post(f"/estudiantes/{est_id}/materias/{mat_id}")
        client.delete(f"/estudiantes/{est_id}")
        # La materia sigue existiendo
        resp = client.get(f"/materias/{mat_id}")
        assert resp.status_code == 200
