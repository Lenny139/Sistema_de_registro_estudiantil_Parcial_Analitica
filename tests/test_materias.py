"""Pruebas de integración para los endpoints de materias.

Implementa: RNF04 (cobertura ≥80%)
Cubre: RF09, RF10
"""

MATERIA_BASE = {
    "nombre": "Cálculo Diferencial",
    "codigo": "MAT-101",
    "creditos": 4,
}


def crear_materia(client, datos=None):
    return client.post("/materias/", json=datos or MATERIA_BASE)


# ── RF09: Crear materia ─────────────────────────────────────────────────────

class TestCrearMateria:
    def test_crea_con_datos_validos(self, client):
        resp = crear_materia(client)
        assert resp.status_code == 201
        body = resp.json()
        assert body["codigo"] == MATERIA_BASE["codigo"]
        assert body["id"] is not None

    def test_falla_creditos_fuera_de_rango(self, client):
        datos = {**MATERIA_BASE, "creditos": 11}
        resp = crear_materia(client, datos)
        assert resp.status_code == 422

    def test_falla_creditos_cero(self, client):
        datos = {**MATERIA_BASE, "creditos": 0}
        resp = crear_materia(client, datos)
        assert resp.status_code == 422

    def test_falla_codigo_duplicado(self, client):
        crear_materia(client)
        datos = {**MATERIA_BASE, "nombre": "Otra materia"}
        resp = crear_materia(client, datos)
        assert resp.status_code == 409

    def test_falla_sin_nombre(self, client):
        datos = {**MATERIA_BASE, "nombre": ""}
        resp = crear_materia(client, datos)
        assert resp.status_code == 422


# ── RF09: Listar materias ───────────────────────────────────────────────────

class TestListarMaterias:
    def test_lista_vacia_al_inicio(self, client):
        resp = client.get("/materias/")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_lista_con_registros(self, client):
        crear_materia(client)
        resp = client.get("/materias/")
        assert len(resp.json()) == 1

    def test_obtener_por_id(self, client):
        id_ = crear_materia(client).json()["id"]
        resp = client.get(f"/materias/{id_}")
        assert resp.status_code == 200
        assert resp.json()["id"] == id_

    def test_retorna_404_si_no_existe(self, client):
        resp = client.get("/materias/9999")
        assert resp.status_code == 404


# ── RF09: Eliminar materia ──────────────────────────────────────────────────

class TestEliminarMateria:
    def test_elimina_exitosamente(self, client):
        id_ = crear_materia(client).json()["id"]
        resp = client.delete(f"/materias/{id_}")
        assert resp.status_code == 204
        assert client.get(f"/materias/{id_}").status_code == 404

    def test_retorna_404_si_no_existe(self, client):
        resp = client.delete("/materias/9999")
        assert resp.status_code == 404
