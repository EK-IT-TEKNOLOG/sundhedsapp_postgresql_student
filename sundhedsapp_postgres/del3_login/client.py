"""Del 3, trin 7: test adgangskontrollen udefra, som en anden app ville gøre.

Start app'en først i en anden terminal (se app.py). Kør derefter:

    uv run client.py
"""

import logging

import requests

logger = logging.getLogger(__name__)

API_URL = "http://127.0.0.1:5001"
LOGINS = {"admin": "admin-pass", "mette": "mette-pass", "nina": "nina-pass"}
ENDPOINTS = [
    ("GET", "/me"),
    ("GET", "/patients"),
    ("GET", "/my_patients"),
    ("DELETE", "/patients/999"),   # findes ikke, så vi sletter ikke rigtige data
]


def login(username: str, password: str) -> str:
    """Log ind, og returnér tokenet."""
    # TODO 7.2: send requests.post(f"{API_URL}/login", json=..., timeout=5)
    #           med en dict {"username": ..., "password": ...}.
    #           Kald response.raise_for_status(), og returnér response.json()["token"].
    raise NotImplementedError("trin 7.2: login")


def status_code(method: str, path: str, token: str | None) -> int:
    """Kald et endpoint med (eller uden) token, og returnér HTTP status code."""
    # TODO 7.3: headers skal være {"Authorization": f"Bearer {token}"}, når der er et token,
    #           og en tom dict {}, når token er None.
    headers = {}
    response = requests.request(method, f"{API_URL}{path}", headers=headers, timeout=5)
    return response.status_code


def log_matrix(tokens: dict[str, str | None]) -> None:
    """Log én linje per endpoint med status code for hver bruger."""
    logger.info("%-22s %s", "", "".join(f"{name:>12}" for name in tokens))
    for method, path in ENDPOINTS:
        codes = "".join(f"{status_code(method, path, token):>12}" for token in tokens.values())
        logger.info("%-22s %s", f"{method} {path}", codes)


def main() -> None:
    """Log ind som hver bruger, og vis, hvilke endpoints de må bruge."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    try:
        tokens: dict[str, str | None] = {
            name: login(name, password) for name, password in LOGINS.items()
        }
        tokens["uden token"] = None
        log_matrix(tokens)

        try:
            login("admin", "forkert")
        except requests.HTTPError as error:
            logger.info("Forkert password giver: %s", error.response.status_code)
    except requests.RequestException as error:
        logger.error("Kunne ikke nå API'et. Kører app'en på port 5001?\n%s", error)


if __name__ == "__main__":
    main()
