"""Del 3, trin 4-6: login, bearer tokens og roller.

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
    # TODO 4.2: hent brugeren med get_user_by_username(username).
    #           Returnér None, hvis brugeren ikke findes, ELLER hvis
    #           check_password_hash(user["password_hash"], password) er False.
    #           Ellers returnér user.
    raise NotImplementedError("trin 4.2: check_login")


def create_token(user_id: int) -> str:
    """Lav et signeret token, der udløber om TOKEN_LIFETIME_SECONDS (færdig)."""
    payload = {"sub": str(user_id), "exp": int(time.time()) + TOKEN_LIFETIME_SECONDS}
    return jwt.encode({"alg": "HS256"}, payload, SECRET_KEY)


def read_token(token: str) -> int | None:
    """Returnér brugerens id, hvis tokenet er ægte og ikke udløbet, ellers None (færdig)."""
    try:
        claims = jwt.decode(token, SECRET_KEY).claims
        REQUIRED_CLAIMS.validate(claims)
    except JoseError:
        return None
    return int(claims["sub"])


@auth.verify_token
def verify_token(token: str) -> dict | None:
    """Kaldes ved hver beskyttet request. None betyder 401 Unauthorized."""
    # TODO 5.2: læs user_id med read_token(token). Er det None, så returnér None.
    #           Ellers returnér get_user(user_id). Den dict bliver til auth.current_user.
    raise NotImplementedError("trin 5.2: verify_token")


@auth.get_user_roles
def get_user_roles(user: dict) -> str:
    """Brugerens rolle. roles=[...] i @app.auth_required sammenligner med den."""
    # TODO 6.1: returnér rollens navn fra user-dict'en. Hvilken key? Se SELECT i get_user.
    raise NotImplementedError("trin 6.1: get_user_roles")
