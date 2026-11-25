"""DocSócios Lite — versão didática e simplificada de um gestor de escalas médicas."""
from flask import Flask, jsonify

from .storage import conectar


def create_app(db_path="docsocios.db"):
    app = Flask(__name__)
    app.config["DB"] = conectar(db_path)

    @app.get("/api/saude")
    def saude():
        return jsonify(status="ok", app="DocSócios Lite")

    return app
