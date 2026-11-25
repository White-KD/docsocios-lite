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
