"""Del 4, trin 4: test databasefunktionerne mod en frisk testdatabase.

Hver test, der beder om fixturen db_url, får sin egen kopi af databasen med de 12 patienter
fra data.sql. Din rigtige database (sundhedsapp) bliver ikke rørt.

    uv run pytest tests/test_database.py -v
"""

import psycopg
import pytest
from psycopg.errors import CheckViolation

from patients import all_patients, delete_patient, patients_of_doctor


def test_all_patients(db_url: str) -> None:
    patients = all_patients()
    assert len(patients) == 12
    assert patients[0]["first_name"] == "Kevin"
    assert patients[0]["doctor_name"] == "Mette Sørensen"   # æ, ø og å skal overleve


def test_patients_of_doctor(db_url: str) -> None:
    # TODO 4.3: lav en liste med first_name for hver patient i patients_of_doctor(1),
    #           og assert, at den er ["Kevin", "Karen", "Erik"].
    raise NotImplementedError("trin 4.3")


def test_delete_patient(db_url: str) -> None:
    # TODO 4.4: tre asserts:
    #           delete_patient(1) er True, delete_patient(1) igen er False,
    #           og der er 11 patienter tilbage.
    raise NotImplementedError("trin 4.4")


def test_database_is_fresh_for_each_test(db_url: str) -> None:
    # TODO 4.5: assert, at der er 12 patienter, selvom testen ovenfor slettede én. Hvorfor virker det?
    raise NotImplementedError("trin 4.5")


def test_database_rejects_bad_blood_type(postgresql: psycopg.Connection) -> None:
    # TODO 4.6: fixturen postgresql er en helt almindelig psycopg-connection til testdatabasen.
    #           Brug pytest.raises(CheckViolation), og kør et INSERT med blodtypen 'X+':
    #           postgresql.execute("INSERT INTO patient (first_name, last_name, age, blood_type, "
    #                              "doctor_id) VALUES ('Test', 'Person', 30, 'X+', 1)")
    raise NotImplementedError("trin 4.6")
