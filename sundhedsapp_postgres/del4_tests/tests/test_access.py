"""Del 4, trin 6: test alle adgangsregler fra del 3 med én parametriseret test.

Det er client.py fra del 3, men nu som en test, der kører automatisk.

    uv run pytest tests/test_access.py -v
"""

from collections.abc import Callable

import pytest
from flask.testing import FlaskClient

Login = Callable[[str], dict[str, str]]


@pytest.mark.parametrize(
    ("method", "path", "username", "expected"),
    [
        ("GET", "/patients", "admin", 200),
        ("GET", "/patients", "nina", 200),
        ("GET", "/patients", "mette", 403),
        # TODO 6.2: tilføj de seks andre rækker fra tabellen i del 3:
        #           GET /my_patients for mette, admin og nina
        #           DELETE /patients/999 for admin, mette og nina
    ],
)
def test_access(
    client: FlaskClient, login: Login, method: str, path: str, username: str, expected: int
) -> None:
    # TODO 6.1: client.open(path, method=method, headers=login(username)) sender en request
    #           med en vilkårlig metode. assert, at status code er expected.
    raise NotImplementedError("trin 6.1")


@pytest.mark.parametrize(
    ("username", "expected"),
    [
        ("mette", ["Kevin", "Karen", "Erik"]),
        # TODO 6.3: jonas (doctor_id 2) har kun Lone.
    ],
)
def test_doctor_sees_only_own_patients(
    client: FlaskClient, login: Login, username: str, expected: list[str]
) -> None:
    # TODO 6.3: hent /my_patients som username, og sammenlign listen af first_name med expected.
    raise NotImplementedError("trin 6.3")
