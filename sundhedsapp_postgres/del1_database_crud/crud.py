"""Del 1, trin 4-6: CRUD på patient-tabellen, én række ad gangen.

Vi skriver queries som t-strings: t"... {value} ..." (Python 3.14 + psycopg 3.3).
psycopg sender hver {value} separat til serveren, så det er sikkert mod SQL injection.

Udfyld TODOs i rækkefølge. Kør filen efter hver funktion:

    uv run crud.py
"""

import logging

import psycopg
from psycopg.errors import CheckViolation

from db import get_connection

logger = logging.getLogger(__name__)


def create_patient(
    first_name: str,
    last_name: str,
    age: int,
    blood_type: str,
    allergies: str | None = None,
) -> int:
    """Indsæt én patient og returnér det id, databasen gav den."""
    # TODO 4.2: gør VALUES-linjen færdig. Sæt hver parameter i {} i samme
    #           rækkefølge som kolonnerne: {first_name}, {last_name}, ...
    query = t"""
        INSERT INTO patient (first_name, last_name, age, blood_type, allergies)
        VALUES ()
        RETURNING patient_id
    """
    with get_connection() as conn:
        # TODO 4.3: kør query med conn.execute(query) og hent rækken med .fetchone()
        #           Rækken er en tuple som (5,). Returnér det første element.
        raise NotImplementedError("trin 4.3: create_patient")


def read_patients() -> list[tuple]:
    """Returnér alle patienter sorteret efter id."""
    with get_connection() as conn:
        return conn.execute("SELECT * FROM patient ORDER BY patient_id").fetchall()


def read_patient(patient_id: int) -> tuple | None:
    """Returnér én patient, eller None hvis id'et ikke findes."""
    # TODO 4.5: skriv en t-string SELECT med WHERE patient_id = {patient_id}
    #           og returnér .fetchone(). Brug read_patients() ovenfor som model.
    raise NotImplementedError("trin 4.5: read_patient")


def update_patient_age(patient_id: int, age: int) -> bool:
    """Ændr en patients alder. Returnér True, hvis en række blev opdateret."""
    # TODO 5.1: t"UPDATE patient SET age = {age} WHERE patient_id = {patient_id}"
    #           Gem den cursor, som conn.execute() returnerer, og
    #           returnér cursor.rowcount == 1 (efter with-blokken).
    raise NotImplementedError("trin 5.1: update_patient_age")


def delete_patient(patient_id: int) -> bool:
    """Slet en patient. Returnér True, hvis en række blev slettet."""
    # TODO 5.2: samme mønster som update_patient_age, med DELETE FROM patient WHERE ...
    raise NotImplementedError("trin 5.2: delete_patient")


def main() -> None:
    """Gå igennem create, read, update og delete for én patient."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    try:
        new_id = create_patient("Anna", "Jensen", 45, "AB+", "Penicillin")
        logger.info("Oprettede patient %s: %s", new_id, read_patient(new_id))

        update_patient_age(new_id, 46)
        logger.info("Efter update:          %s", read_patient(new_id))

        delete_patient(new_id)
        logger.info("Efter delete:          %s", read_patient(new_id))

        # TODO 6.1: prøv at oprette en patient med blodtype "X+".
        # TODO 6.2: pak kaldet ind i try / except CheckViolation as error:
        #           og log error.diag.message_primary med logger.warning(...)

        logger.info("Alle patienter:")
        for patient in read_patients():
            logger.info("  %s", patient)
    except psycopg.OperationalError as error:
        logger.error("Kunne ikke forbinde til PostgreSQL:\n%s", error)


if __name__ == "__main__":
    main()
