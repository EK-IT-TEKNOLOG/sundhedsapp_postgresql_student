"""Del 3, trin 4-6: sundhedsappen med login og role-based access control.

Start fra mappen del3_login (lektion 4-appen bruger port 5000, så vi bruger 5001):

    uv run flask --app app run --port 5001 --debug

--debug genstarter serveren, hver gang du gemmer en fil. Åbn http://127.0.0.1:5001/docs
"""

import logging

import psycopg
from apiflask import APIFlask, Schema, abort
from apiflask.fields import String

from auth import auth, check_login, create_token
from patients import all_patients, delete_patient, patients_of_doctor

logger = logging.getLogger(__name__)

app = APIFlask(__name__, title="Sundhedsapp med login")


class LoginIn(Schema):
    username = String(required=True)
    password = String(required=True)


class TokenOut(Schema):
    token = String()


@app.errorhandler(psycopg.Error)
def database_error(error: psycopg.Error) -> tuple[dict, int]:
    """Vis aldrig databasens fejlbesked til klienten. Log den i stedet."""
    logger.error("Databasefejl: %s", error)
    return {"message": "Databasefejl"}, 500


@app.post("/login")
@app.input(LoginIn)
@app.output(TokenOut)
def login(json_data: dict) -> dict:
    """Log ind med brugernavn og password, og få et bearer token."""
    # TODO 4.3: kald check_login med json_data["username"] og json_data["password"].
    #           Er resultatet None: abort(401, "Forkert brugernavn eller password").
    #           Ellers: return {"token": create_token(user["user_id"])}
    raise NotImplementedError("trin 4.3: login")


@app.get("/me")
@app.auth_required(auth)
def me() -> dict:
    """Hvem er jeg logget ind som? Alle roller."""
    user = auth.current_user
    return {"username": user["username"], "role": user["role_name"]}


# TODO 6.2: tilføj roles=[...] til @app.auth_required på de tre endpoints nedenfor:
#           /patients      -> admin og nurse
#           /my_patients   -> doctor
#           DELETE         -> admin
#           Eksempel: @app.auth_required(auth, roles=["admin", "nurse"])


@app.get("/patients")
@app.auth_required(auth)
def patients() -> list[dict]:
    """Alle patienter. Kun admin og nurse."""
    return all_patients()


@app.get("/my_patients")
@app.auth_required(auth)
def my_patients() -> list[dict]:
    """Kun den indloggede læges egne patienter."""
    return patients_of_doctor(auth.current_user["doctor_id"])


@app.delete("/patients/<int:patient_id>")
@app.auth_required(auth)
def remove_patient(patient_id: int) -> tuple[str, int]:
    """Slet en patient. Kun admin."""
    if not delete_patient(patient_id):
        abort(404, "Patienten findes ikke")
    return "", 204
