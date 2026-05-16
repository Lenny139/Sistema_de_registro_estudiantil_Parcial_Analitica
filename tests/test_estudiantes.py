"""Pruebas de integración para los endpoints de estudiantes.

Implementa: RNF04 (cobertura ≥80%, pruebas por endpoint)
Cubre: RF01, RF02, RF03, RF04, RF05, RF06, RF10
"""

import pytest

ESTUDIANTE_BASE = {
    "nombre": "Ana Torres",
    "codigo": "EST-001",
    "email": "ana.torres@uni.edu",
    "carrera": "Ingeniería de Sistemas",
    "semestre": 4,
}


def crear_estudiante(client, datos=None):
    """Helper para crear un estudiante en las pruebas."""
    return client.post("/estudiantes/", json=datos or ESTUDIANTE_BASE)


# ── RF01: Crear estudiante ──────────────────────────────────────────────────

class TestCrearEstudiante:
    def test_crea_con_datos_validos(self, client):
        resp = crear_estudiante(client)
        assert resp.status_code == 201
        body = resp.json()
        assert body["email"] == ESTUDIANTE_BASE["email"]
        assert body["id"] is not None

    def test_falla_sin_nombre(self, client):
        datos = {**ESTUDIANTE_BASE, "nombre": ""}
        resp = crear_estudiante(client, datos)
        assert resp.status_code == 422

    def test_falla_semestre_fuera_de_rango(self, client):
        datos = {**ESTUDIANTE_BASE, "semestre": 15}
        resp = crear_estudiante(client, datos)
        assert resp.status_code == 422

    def test_falla_email_invalido(self, client):
        datos = {**ESTUDIANTE_BASE, "email": "no-es-un-email"}
        resp = crear_estudiante(client, datos)
        assert resp.status_code == 422

    def test_falla_email_duplicado(self, client):
        crear_estudiante(client)
        datos = {**ESTUDIANTE_BASE, "codigo": "EST-002"}
        resp = crear_estudiante(client, datos)
        assert resp.status_code == 409
        assert "email" in resp.json()["detail"].lower()

    def test_falla_codigo_duplicado(self, client):
        crear_estudiante(client)
        datos = {**ESTUDIANTE_BASE, "email": "otro@uni.edu"}
        resp = crear_estudiante(client, datos)
        assert resp.status_code == 409
        assert "código" in resp.json()["detail"].lower()


# ── RF02: Obtener por ID ────────────────────────────────────────────────────

class TestObtenerEstudiantePorId:
    def test_retorna_estudiante_existente(self, client):
        id_ = crear_estudiante(client).json()["id"]
        resp = client.get(f"/estudiantes/{id_}")
        assert resp.status_code == 200
        assert resp.json()["id"] == id_

    def test_retorna_404_si_no_existe(self, client):
        resp = client.get("/estudiantes/9999")
        assert resp.status_code == 404


# ── RF03: Buscar por nombre ─────────────────────────────────────────────────

class TestBuscarPorNombre:
    def test_encuentra_por_nombre_parcial(self, client):
        crear_estudiante(client)
        resp = client.get("/estudiantes/?nombre=ana")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_busqueda_case_insensitive(self, client):
        crear_estudiante(client)
        resp = client.get("/estudiantes/?nombre=ANA")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_retorna_lista_vacia_si_no_hay_coincidencia(self, client):
        crear_estudiante(client)
        resp = client.get("/estudiantes/?nombre=zzznoencontrado")
        assert resp.status_code == 200
        assert resp.json() == []


# ── RF04: Actualizar estudiante ─────────────────────────────────────────────

class TestActualizarEstudiante:
    def test_actualiza_campo_individual(self, client):
        id_ = crear_estudiante(client).json()["id"]
        resp = client.patch(f"/estudiantes/{id_}", json={"semestre": 7})
        assert resp.status_code == 200
        assert resp.json()["semestre"] == 7

    def test_no_modifica_campos_no_enviados(self, client):
        id_ = crear_estudiante(client).json()["id"]
        client.patch(f"/estudiantes/{id_}", json={"semestre": 7})
        resp = client.get(f"/estudiantes/{id_}")
        assert resp.json()["nombre"] == ESTUDIANTE_BASE["nombre"]

    def test_retorna_404_si_no_existe(self, client):
        resp = client.patch("/estudiantes/9999", json={"semestre": 5})
        assert resp.status_code == 404

    def test_falla_semestre_invalido(self, client):
        id_ = crear_estudiante(client).json()["id"]
        resp = client.patch(f"/estudiantes/{id_}", json={"semestre": 0})
        assert resp.status_code == 422


# ── RF05: Eliminar estudiante ───────────────────────────────────────────────

class TestEliminarEstudiante:
    def test_elimina_exitosamente(self, client):
        id_ = crear_estudiante(client).json()["id"]
        resp = client.delete(f"/estudiantes/{id_}")
        assert resp.status_code == 204
        assert client.get(f"/estudiantes/{id_}").status_code == 404

    def test_retorna_404_si_no_existe(self, client):
        resp = client.delete("/estudiantes/9999")
        assert resp.status_code == 404


# ── RF06: Listar estudiantes ────────────────────────────────────────────────

class TestListarEstudiantes:
    def test_lista_vacia_al_inicio(self, client):
        resp = client.get("/estudiantes/")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_lista_con_registros(self, client):
        crear_estudiante(client)
        resp = client.get("/estudiantes/")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_paginacion_con_skip_y_limit(self, client):
        for i in range(3):
            client.post("/estudiantes/", json={**ESTUDIANTE_BASE, "codigo": f"EST-{i}", "email": f"est{i}@uni.edu"})
        resp = client.get("/estudiantes/?skip=1&limit=1")
        assert resp.status_code == 200
        assert len(resp.json()) == 1
