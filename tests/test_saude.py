def test_endpoint_de_saude_responde_ok(client):
    resp = client.get("/api/saude")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"
