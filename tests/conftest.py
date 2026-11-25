import pytest

from app import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app(db_path=str(tmp_path / "teste.db"))
    app.config["TESTING"] = True
    return app.test_client()
