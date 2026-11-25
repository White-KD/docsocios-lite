"""Regras de negócio do DocSócios Lite (independentes do Flask, fáceis de testar)."""
import re


class ErroValidacao(ValueError):
    """Erro de regra de negócio que deve virar resposta HTTP 400/409."""

    def __init__(self, mensagem, status=400):
        super().__init__(mensagem)
        self.status = status


CRM_REGEX = re.compile(r"^\d{4,6}-[A-Z]{2}$")


def normalizar_crm(crm):
    return (crm or "").strip().upper().replace(" ", "").replace("/", "-")


# ---------------------------------------------------------------- Médicos
def cadastrar_medico(conn, nome, crm):
    nome = (nome or "").strip()
    crm = normalizar_crm(crm)
    if len(nome) < 3:
        raise ErroValidacao("Informe o nome completo do médico.")
    if not CRM_REGEX.match(crm):
        raise ErroValidacao("CRM inválido. Use o formato 12345-PR.")
    if conn.execute("SELECT 1 FROM medicos WHERE crm = ?", (crm,)).fetchone():
        raise ErroValidacao(f"Já existe um médico com o CRM {crm}.", status=409)
    cur = conn.execute("INSERT INTO medicos (nome, crm) VALUES (?, ?)", (nome, crm))
    conn.commit()
    return {"id": cur.lastrowid, "nome": nome, "crm": crm}


def listar_medicos(conn):
    rows = conn.execute("SELECT id, nome, crm FROM medicos ORDER BY nome").fetchall()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------- Plantões
TURNOS = {"D": "Diurno (07h-19h)", "N": "Noturno (19h-07h)"}
DATA_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def registrar_plantao(conn, medico_id, data, turno, valor):
    turno = (turno or "").strip().upper()
    if not conn.execute("SELECT 1 FROM medicos WHERE id = ?", (medico_id,)).fetchone():
        raise ErroValidacao("Médico não encontrado.", status=404)
    if not DATA_REGEX.match(data or ""):
        raise ErroValidacao("Data inválida. Use AAAA-MM-DD.")
    if turno not in TURNOS:
        raise ErroValidacao("Turno inválido. Use D (diurno) ou N (noturno).")
    try:
        valor = float(valor)
    except (TypeError, ValueError):
        raise ErroValidacao("Valor do plantão inválido.")
    if valor <= 0:
        raise ErroValidacao("O valor do plantão deve ser maior que zero.")

    ocupado = conn.execute(
        "SELECT m.nome FROM plantoes p JOIN medicos m ON m.id = p.medico_id "
        "WHERE p.data = ? AND p.turno = ?",
        (data, turno),
    ).fetchone()
    if ocupado:
        raise ErroValidacao(
            f"Conflito de escala: {data} turno {turno} já está com {ocupado['nome']}.",
            status=409,
        )

    cur = conn.execute(
        "INSERT INTO plantoes (medico_id, data, turno, valor) VALUES (?, ?, ?, ?)",
        (medico_id, data, turno, valor),
    )
    conn.commit()
    return {"id": cur.lastrowid, "medico_id": medico_id, "data": data,
            "turno": turno, "valor": valor}


def listar_escala(conn, mes=None):
    sql = ("SELECT p.id, p.data, p.turno, p.valor, m.nome AS medico, m.crm "
           "FROM plantoes p JOIN medicos m ON m.id = p.medico_id")
    params = ()
    if mes:
        sql += " WHERE substr(p.data, 1, 7) = ?"
        params = (mes,)
    sql += " ORDER BY p.data, p.turno"
    return [dict(r) for r in conn.execute(sql, params).fetchall()]
