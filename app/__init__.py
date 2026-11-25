"""DocSócios Lite — versão didática e simplificada de um gestor de escalas médicas."""
from flask import Flask, jsonify, render_template, request

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

    @app.get("/")
    def inicio():
        return render_template("index.html")

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

    # ---------------------------------------------------------- Plantões
    @app.get("/api/plantoes")
    def listar_plantoes():
        return jsonify(services.listar_escala(db(), request.args.get("mes")))

    @app.post("/api/plantoes")
    def registrar_plantao():
        d = request.get_json(silent=True) or {}
        plantao = services.registrar_plantao(
            db(), d.get("medico_id"), d.get("data"), d.get("turno"), d.get("valor"))
        return jsonify(plantao), 201

    # ---------------------------------------------------------- Repasse
    @app.get("/api/repasse")
    def repasse():
        mes = request.args.get("mes")
        taxa = request.args.get("taxa", services.TAXA_ADMIN_PADRAO)
        return jsonify(services.calcular_repasse(db(), mes, taxa))

    return app
