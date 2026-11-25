def test_cadastra_medico_e_normaliza_crm(client):
    resp = client.post("/api/medicos", json={"nome": "Ana Souza", "crm": " 58363/pr "})
    assert resp.status_code == 201
    assert resp.get_json()["crm"] == "58363-PR"

    lista = client.get("/api/medicos").get_json()
    assert [m["nome"] for m in lista] == ["Ana Souza"]


def test_rejeita_crm_em_formato_invalido(client):
    resp = client.post("/api/medicos", json={"nome": "Ana Souza", "crm": "abc"})
    assert resp.status_code == 400
    assert "CRM inválido" in resp.get_json()["erro"]


def test_nao_permite_crm_duplicado(client):
    client.post("/api/medicos", json={"nome": "Ana Souza", "crm": "11111-PR"})
    resp = client.post("/api/medicos", json={"nome": "Outro Nome", "crm": "11111-PR"})
    assert resp.status_code == 409
