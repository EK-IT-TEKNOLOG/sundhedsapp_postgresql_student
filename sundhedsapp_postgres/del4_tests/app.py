"""Del 4 (færdig fra del 3): sundhedsappen med login og role-based access control.

Du skal ikke ændre denne fil i del 4: testene kører den med Flasks test client.

Vil du alligevel starte den: uv run flask --app app run --port 5001

Åbn derefter http://127.0.0.1:5001/docs
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
    user = check_login(json_data["username"], json_data["password"])
    if user is None:
        abort(401, "Forkert brugernavn eller password")
    return {"token": create_token(user["user_id"])}


@app.get("/me")
@app.auth_required(auth)
def me() -> dict:
    """Hvem er jeg logget ind som? Alle roller."""
    user = auth.current_user
    return {"username": user["username"], "role": user["role_name"]}


@app.get("/patients")
@app.auth_required(auth, roles=["admin", "nurse"])
def patients() -> list[dict]:
    """Alle patienter. Kun admin og nurse."""
    return all_patients()


@app.get("/my_patients")
@app.auth_required(auth, roles=["doctor"])
def my_patients() -> list[dict]:
    """Kun den indloggede læges egne patienter."""
    return patients_of_doctor(auth.current_user["doctor_id"])


@app.delete("/patients/<int:patient_id>")
@app.auth_required(auth, roles=["admin"])
def remove_patient(patient_id: int) -> tuple[str, int]:
    """Slet en patient. Kun admin."""
    if not delete_patient(patient_id):
        abort(404, "Patienten findes ikke")
    return "", 204
