"""Del 1, trin 7: mange rækker på én gang med executemany().

Patienterne hentes fra API'et fra lektion 4 med et bearer token.
Start appen fra lektion 4 først (sundhedsapp/del4 visualisering: flask run).

Hvorfor %s her og ikke t-strings? En t-string fanger værdierne for ÉN række, når den
oprettes. executemany() skal bruge én query med tomme pladser (%s) plus en liste af rækker
at fylde dem med.

    uv run bulk.py
"""

import logging

import psycopg
import requests

from crud import read_patients
from db import get_connection

logger = logging.getLogger(__name__)

API_URL = "http://127.0.0.1:5000"
NO_ALLERGY = {"", "no", "none", "false"}

# Én patient som en række: (first_name, last_name, age, blood_type, allergies)
PatientRow = tuple[str, str, int, str, str | None]


def get_token(user_id: int = 1) -> str:
    """Bed API'et om et token. API'et returnerer det som 'Bearer <token>'."""
    response = requests.post(f"{API_URL}/token/{user_id}", timeout=5)
    response.raise_for_status()
    return response.json()["token"]


def fetch_patients(token: str) -> dict[str, dict]:
    """Hent alle patienter fra det beskyttede /health_data endpoint."""
    # TODO 7.4: lav en headers-dict med token: {"Authorization": token}
    #           (se post_api_bearer_token.py fra lektion 4).
    # TODO 7.5: requests.get(f"{API_URL}/health_data", headers=headers, timeout=5),
    #           kald response.raise_for_status() og
    #           returnér response.json()["patients"]["id"]
    raise NotImplementedError("trin 7.4: fetch_patients")


def clean_allergies(value: str | bool | None) -> str | None:
    """YAML-filen blander False, 'No' og rigtige allergier. Gem 'ingen' som NULL."""
    if value is None or value is False or str(value).strip().lower() in NO_ALLERGY:
        return None
    return str(value)


def to_row(patient: dict) -> PatientRow:
    """Lav én patient-dict fra API'et om til en række til patient-tabellen."""
    # /add_patient i lektion 4 gemmer "bloodtype", patient.yml bruger "blood_type".
    blood_type = patient.get("blood_type") or patient.get("bloodtype")
    return (
        patient["first_name"],
        patient["last_name"],
        patient["age"],
        blood_type,
        clean_allergies(patient.get("allergies")),
    )


def clear_patients() -> None:
    """Fjern alle patienter og start id-tælleren forfra ved 1."""
    with get_connection() as conn:
        conn.execute("TRUNCATE patient RESTART IDENTITY")


def insert_patients(rows: list[PatientRow]) -> int:
    """Indsæt mange patienter i ét kald. Returnér antallet af indsatte rækker."""
    sql = """
        INSERT INTO patient (first_name, last_name, age, blood_type, allergies)
        VALUES (%s, %s, %s, %s, %s)
    """
    with get_connection() as conn, conn.cursor() as cursor:
        cursor.executemany(sql, rows)
        return cursor.rowcount


def update_ages(changes: list[tuple[int, int]]) -> int:
    """Opdatér mange aldre. Hver ændring er (new_age, patient_id)."""
    # TODO 7.7: kopiér kroppen af insert_patients og ændr SQL'en til
    #           UPDATE patient SET age = %s WHERE patient_id = %s
    #           Hver tuple i changes udfylder de to %s i rækkefølge: (new_age, patient_id)
    raise NotImplementedError("trin 7.7: update_ages")


def delete_patients(patient_ids: list[int]) -> int:
    """Slet mange patienter ud fra id."""
    # TODO 7.8: executemany skal bruge en liste af tuples, ikke en liste af ints.
    #           Lav [3, 4] om til [(3,), (4,)] med en list comprehension,
    #           og kør derefter DELETE FROM patient WHERE patient_id = %s
    raise NotImplementedError("trin 7.8: delete_patients")


def log_patients(title: str) -> None:
    """Log alle patienter i tabellen under en overskrift."""
    logger.info(title)
    for patient in read_patients():
        logger.info("  %s", patient)


def main() -> None:
    """Importér patienter fra API'et, og opdatér og slet derefter flere på én gang."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    try:
        patients = fetch_patients(get_token())
    except requests.RequestException as error:
        logger.error("Kunne ikke nå API'et. Kører appen fra lektion 4?\n%s", error)
        return

    rows = [to_row(patient) for patient in patients.values()]
    try:
        clear_patients()
        logger.info("Indsatte %d patienter", insert_patients(rows))
        log_patients("Efter insert:")

        logger.info("Opdaterede %d patienter", update_ages([(35, 1), (67, 2)]))
        log_patients("Efter update:")

        logger.info("Slettede %d patienter", delete_patients([3, 4]))
        log_patients("Efter delete:")
    except psycopg.Error as error:
        logger.error("Databasefejl:\n%s", error)


if __name__ == "__main__":
    main()
