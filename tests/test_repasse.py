def _escala(client):
    ana = client.post("/api/medicos", json={"nome": "Ana Souza", "crm": "11111-PR"}).get_json()["id"]
    bruno = client.post("/api/medicos", json={"nome": "Bruno Lima", "crm": "22222-PR"}).get_json()["id"]
    for data, turno, mid, valor in [
        ("2026-12-01", "D", ana, 1000), ("2026-12-01", "N", bruno, 1500),
        ("2026-12-02", "D", ana, 1000), ("2027-01-01", "D", ana, 9999),
    ]:
        client.post("/api/plantoes", json={"medico_id": mid, "data": data, "turno": turno, "valor": valor})


def test_repasse_soma_plantoes_do_mes_e_desconta_taxa_de_10_porcento(client):
    _escala(client)
    rep = {r["medico"]: r for r in client.get("/api/repasse?mes=2026-12").get_json()}
    assert rep["Ana Souza"]["plantoes"] == 2
    assert rep["Ana Souza"]["bruto"] == 2000.0
    assert rep["Ana Souza"]["liquido"] == 1800.0
    assert rep["Bruno Lima"]["taxa"] == 150.0


def test_repasse_sem_taxa_repassa_valor_integral(client):
    _escala(client)
    rep = client.get("/api/repasse?mes=2026-12&taxa=0").get_json()
    assert all(r["liquido"] == r["bruto"] for r in rep)


def test_repasse_rejeita_mes_invalido(client):
    assert client.get("/api/repasse?mes=12-2026").status_code == 400
