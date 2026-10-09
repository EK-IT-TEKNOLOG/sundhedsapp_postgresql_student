"""Del 4: fixtures, som alle tests i mappen kan bruge.

pytest finder conftest.py automatisk. En test får en fixture ved at nævne den som parameter.
"""

from collections.abc import Callable
from pathlib import Path

import psycopg
import pytest
from flask.testing import FlaskClient
from psycopg.conninfo import conninfo_to_dict, make_conninfo
from pytest_postgresql import factories

import db
from app import app
from users import TEST_USERS, create_users

FOLDER = Path(__file__).parent.parent
SERVER = conninfo_to_dict(db.DATABASE_URL)
PASSWORDS = {username: password for username, password, _role, _doctor in TEST_USERS}


# --- Trin 4: en frisk database til hver test ---------------------------------------

def load_test_data(
    host: str, port: int, user: str, dbname: str, password: str | None = None, **_: object
) -> None:
    """Fyld skabelon-databasen. Kører kun én gang per testkørsel, ikke én gang per test."""
    url = make_conninfo(host=host, port=port, user=user, dbname=dbname, password=password)
    with psycopg.connect(url) as conn:
        for name in ("schema.sql", "data.sql"):
            conn.execute((FOLDER / name).read_text(encoding="utf-8"))
    # create_users() bruger db.DATABASE_URL, så vi peger den kort på skabelonen.
    # Hashing af passwords er langsomt med vilje, så det skal kun ske én gang.
    original_url = db.DATABASE_URL
    db.DATABASE_URL = url
    try:
        create_users(TEST_USERS)
    finally:
        db.DATABASE_URL = original_url


# Brug den PostgreSQL-server, du allerede har (password fra db.py), men en anden database.
# load_test_data fylder en skabelon, og hver test får sin egen kopi af den.
postgresql_server = factories.postgresql_noproc(
    host=SERVER.get("host"),
    port=SERVER.get("port"),
    user=SERVER.get("user"),
    password=SERVER.get("password"),
    dbname="sundhedsapp_test",
    load=[load_test_data],
)
postgresql = factories.postgresql("postgresql_server")


@pytest.fixture
def db_url(postgresql, monkeypatch: pytest.MonkeyPatch) -> str:
    """Peg db.get_connection() på testdatabasen i stedet for din rigtige database."""
    info = postgresql.info
    url = make_conninfo(
        host=info.host, port=info.port, user=info.user, password=info.password, dbname=info.dbname
    )
    monkeypatch.setattr(db, "DATABASE_URL", url)
    return url


# --- Trin 5: login ---------------------------------------------------------------


@pytest.fixture
def client(db_url: str) -> FlaskClient:
    """En Flask test client: send requests til app'en uden at starte en server."""
    app.testing = True
    return app.test_client()


@pytest.fixture
def login(client: FlaskClient) -> Callable[[str], dict[str, str]]:
    """Returnér en funktion: login("mette") giver headers med et gyldigt token."""

    def _login(username: str) -> dict[str, str]:
        # TODO 5.1: 1) lav credentials: {"username": username, "password": PASSWORDS[username]}
        #           2) response = client.post("/login", json=credentials)
        #           3) assert response.status_code == 200
        #           4) return {"Authorization": f"Bearer {response.json['token']}"}
        raise NotImplementedError("trin 5.1: login-fixturen")

    return _login
