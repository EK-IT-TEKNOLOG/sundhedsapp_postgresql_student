"""Del 4 (færdig fra del 3): login, bearer tokens og roller.

Et token er en JWT med brugerens id ("sub") og et udløbstidspunkt ("exp"), signeret med
SECRET_KEY. Rollen står ikke i tokenet: vi slår brugeren op i databasen ved hver request,
så en ændret rolle virker med det samme.
"""

import secrets
import time

from apiflask import HTTPTokenAuth
from joserfc import jwt
from joserfc.errors import JoseError
from joserfc.jwk import OctKey
from werkzeug.security import check_password_hash

from users import get_user, get_user_by_username

TOKEN_LIFETIME_SECONDS = 30 * 60

# Ny nøgle, hver gang serveren starter, så alle gamle tokens bliver ugyldige ved genstart.
# I produktion læser man nøglen fra en environment variabel.
SECRET_KEY = OctKey.import_key(secrets.token_bytes(32))
REQUIRED_CLAIMS = jwt.JWTClaimsRegistry(exp={"essential": True})

auth = HTTPTokenAuth(scheme="Bearer")


def check_login(username: str, password: str) -> dict | None:
    """Returnér brugeren, hvis brugernavn og password passer, ellers None."""
    user = get_user_by_username(username)
    if user is None or not check_password_hash(user["password_hash"], password):
        return None
    return user


def create_token(user_id: int) -> str:
    """Lav et signeret token, der udløber om TOKEN_LIFETIME_SECONDS."""
    payload = {"sub": str(user_id), "exp": int(time.time()) + TOKEN_LIFETIME_SECONDS}
    return jwt.encode({"alg": "HS256"}, payload, SECRET_KEY)


def read_token(token: str) -> int | None:
    """Returnér brugerens id, hvis tokenet er ægte og ikke udløbet, ellers None."""
    try:
        claims = jwt.decode(token, SECRET_KEY).claims
        REQUIRED_CLAIMS.validate(claims)
    except JoseError:
        return None
    return int(claims["sub"])


@auth.verify_token
def verify_token(token: str) -> dict | None:
    """Kaldes ved hver beskyttet request. None betyder 401 Unauthorized."""
    user_id = read_token(token)
    if user_id is None:
        return None
    return get_user(user_id)


@auth.get_user_roles
def get_user_roles(user: dict) -> str:
    """Brugerens rolle. roles=[...] i @app.auth_required sammenligner med den."""
    return user["role_name"]
