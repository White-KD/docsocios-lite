"""DocSócios Lite — versão didática e simplificada de um gestor de escalas médicas."""
from flask import Flask, jsonify, request

from . import services
from .storage import conectar


def create_app(db_path="docsocios.db"):
    app = Flask(__name__)
    app.config["DB"] = conectar(db_path)

    def db():
        return app.config["DB"]

    @app.errorhandler(services.ErroValidacao)
    def erro_validacao(e):
        return jsonify(erro=str(e)), e.status

    @app.get("/api/saude")
    def saude():
        return jsonify(status="ok", app="DocSócios Lite")

    # ---------------------------------------------------------- Médicos
    @app.get("/api/medicos")
    def listar_medicos():
        return jsonify(services.listar_medicos(db()))

    @app.post("/api/medicos")
    def cadastrar_medico():
        dados = request.get_json(silent=True) or {}
        medico = services.cadastrar_medico(db(), dados.get("nome"), dados.get("crm"))
        return jsonify(medico), 201

    return app
