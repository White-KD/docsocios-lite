def _medico(client, nome="Ana Souza", crm="11111-PR"):
    return client.post("/api/medicos", json={"nome": nome, "crm": crm}).get_json()["id"]


def test_registra_plantao_e_lista_na_escala_do_mes(client):
    mid = _medico(client)
    resp = client.post("/api/plantoes", json={
        "medico_id": mid, "data": "2026-12-05", "turno": "n", "valor": 1500})
    assert resp.status_code == 201

    escala = client.get("/api/plantoes?mes=2026-12").get_json()
    assert len(escala) == 1
    assert escala[0]["medico"] == "Ana Souza" and escala[0]["turno"] == "N"
    assert client.get("/api/plantoes?mes=2027-01").get_json() == []


def test_bloqueia_conflito_de_escala_no_mesmo_turno(client):
    ana = _medico(client)
    bruno = _medico(client, "Bruno Lima", "22222-PR")
    client.post("/api/plantoes", json={
        "medico_id": ana, "data": "2026-12-05", "turno": "D", "valor": 1200})
    resp = client.post("/api/plantoes", json={
        "medico_id": bruno, "data": "2026-12-05", "turno": "D", "valor": 1200})
    assert resp.status_code == 409
    assert "Conflito de escala" in resp.get_json()["erro"]


def test_rejeita_plantao_com_valor_ou_turno_invalido(client):
    mid = _medico(client)
    base = {"medico_id": mid, "data": "2026-12-05"}
    assert client.post("/api/plantoes", json={**base, "turno": "X", "valor": 100}).status_code == 400
    assert client.post("/api/plantoes", json={**base, "turno": "D", "valor": -5}).status_code == 400
