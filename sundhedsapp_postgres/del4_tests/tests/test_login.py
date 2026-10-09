"""Del 4, trin 5: test login med fixtures.

Fixturen client giver en Flask test client, der taler med app'en uden en rigtig server.
Fixturen login (conftest.py) logger ind og giver dig headers med et token.

    uv run pytest tests/test_login.py -v
"""

from collections.abc import Callable

from flask.testing import FlaskClient

WRONG_LOGIN = "Forkert brugernavn eller password"


def test_login_returns_token(client: FlaskClient) -> None:
    response = client.post("/login", json={"username": "mette", "password": "mette-pass"})
    assert response.status_code == 200
    assert "token" in response.json


def test_login_wrong_password(client: FlaskClient) -> None:
    # TODO 5.2: log ind som mette med et forkert password. assert status 401,
    #           og at response.json["message"] er WRONG_LOGIN.
    raise NotImplementedError("trin 5.2")


def test_login_unknown_user_gives_same_message(client: FlaskClient) -> None:
    # TODO 5.3: det samme med en bruger, der ikke findes. Samme status, samme besked.
    raise NotImplementedError("trin 5.3")


def test_me_without_token(client: FlaskClient) -> None:
    # TODO 5.4: client.get("/me") uden headers skal give 401.
    raise NotImplementedError("trin 5.4")


def test_me_with_token(client: FlaskClient, login: Callable[[str], dict[str, str]]) -> None:
    # TODO 5.5: response = client.get("/me", headers=login("mette"))
    #           assert status 200, og at response.json er {"username": "mette", "role": "doctor"}.
    raise NotImplementedError("trin 5.5")
