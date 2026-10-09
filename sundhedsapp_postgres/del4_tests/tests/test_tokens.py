"""Del 4, trin 3: test tokens uden database og uden server.

    uv run pytest tests/test_tokens.py -v
"""

import base64
import json

import pytest

import auth
from auth import create_token, read_token


def forge_payload(token: str, user_id: int) -> str:
    """Byt payload ud med en, hvor sub er et andet id. Signaturen er stadig den gamle (færdig)."""
    header, _payload, signature = token.split(".")
    fake = json.dumps({"sub": str(user_id), "exp": 9999999999}).encode()
    payload = base64.urlsafe_b64encode(fake).decode().rstrip("=")
    return f"{header}.{payload}.{signature}"


def test_token_roundtrip() -> None:
    token = create_token(7)
    assert read_token(token) == 7


def test_forged_token_is_rejected() -> None:
    # TODO 3.2: lav et token til bruger 2, og brug forge_payload til at gøre det til bruger 1.
    #           assert, at read_token(...) giver None. (Kan mette gøre sig selv til admin?)
    raise NotImplementedError("trin 3.2")


def test_garbage_is_rejected() -> None:
    # TODO 3.3: read_token("ikke et token") skal give None, ikke en exception.
    raise NotImplementedError("trin 3.3")


def test_expired_token_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    # TODO 3.4: vi vil ikke vente 30 minutter. Gør tokenet udløbet fra starten:
    #               monkeypatch.setattr(auth, "TOKEN_LIFETIME_SECONDS", -1)
    #           Lav derefter et token, og assert, at read_token giver None.
    #           monkeypatch sætter værdien tilbage, når testen er færdig.
    raise NotImplementedError("trin 3.4")
