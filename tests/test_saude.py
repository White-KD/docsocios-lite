def test_endpoint_de_saude_responde_ok(client):
    resp = client.get("/api/saude")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_pagina_inicial_carrega_interface(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "DocSócios Lite" in resp.get_data(as_text=True)
