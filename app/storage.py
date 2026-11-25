"""Camada de persistência simples em SQLite (biblioteca padrão do Python)."""
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS medicos (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    crm  TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS plantoes (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    medico_id INTEGER NOT NULL REFERENCES medicos(id),
    data      TEXT NOT NULL,
    turno     TEXT NOT NULL,
    valor     REAL NOT NULL
);
"""


def conectar(caminho):
    conn = sqlite3.connect(caminho, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn
