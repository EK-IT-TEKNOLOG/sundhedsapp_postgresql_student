"""Del 2, trin 3: fyld hospital, doctor og patient med executemany().

Hospitaler og læger står i listerne nedenfor. Patienterne hentes fra API'et fra lektion 4
med et bearer token (api.py), og hver patient får en læge.

Rækkefølgen betyder noget: en læge peger på et hospital, og en patient peger på en læge.
Derfor indsætter vi hospital -> doctor -> patient, og alt sker i én transaction.

Udfyld TODOs i rækkefølge, og kør filen:

    uv run seed.py
"""

import logging
from datetime import date

import psycopg

from api import clean_allergies, load_patients
from db import get_connection

logger = logging.getLogger(__name__)

# (hospital_name, bed_count)
HospitalRow = tuple[str, int]
# (doctor_name, hospital_id, joining_date, speciality, salary, experience)
DoctorRow = tuple[str, int, date, str, int, int | None]
# (first_name, last_name, age, blood_type, allergies, doctor_id)
PatientRow = tuple[str, str, int, str, str | None, int]

# IDENTITY giver id'erne 1, 2, 3 ... i den rækkefølge, rækkerne indsættes.
HOSPITALS: list[HospitalRow] = [
    ("Rigshospitalet", 1100),                # 1
    ("Aarhus Universitetshospital", 1150),   # 2
    ("Odense Universitetshospital", 1000),   # 3
    ("Aalborg Universitetshospital", 600),   # 4
    ("Bornholms Hospital", 90),              # 5  (ingen læger endnu)
]

DOCTORS: list[DoctorRow] = [
    ("Mette Sørensen", 1, date(2015, 3, 1), "Kardiologi", 72000, 12),        # 1
    ("Jonas Madsen", 1, date(2021, 8, 15), "Kardiologi", 58000, 4),          # 2
    ("Sara Nielsen", 1, date(2019, 1, 10), "Pædiatri", 61000, 7),            # 3
    ("Ali Hassan", 2, date(2012, 6, 1), "Ortopædkirurgi", 78000, 15),        # 4
    ("Emma Kristensen", 2, date(2023, 2, 1), "Pædiatri", 52000, None),       # 5
    ("Peter Larsen", 2, date(2017, 9, 1), "Kardiologi", 69000, 9),           # 6
    ("Freja Andersen", 3, date(2020, 4, 1), "Ortopædkirurgi", 64000, 6),     # 7
    ("Oliver Poulsen", 3, date(2024, 1, 15), "Almen medicin", 50000, None),  # 8
    ("Ida Rasmussen", 4, date(2016, 11, 1), "Almen medicin", 60000, 10),     # 9
]

# Flere patienter end de fire fra lektion 4, så GROUP BY har noget at arbejde med.
EXTRA_PATIENTS: list[PatientRow] = [
    ("Sofie", "Berg", 8, "A+", None, 3),
    ("Noah", "Friis", 5, "O+", "Gluten", 5),
    ("Karen", "Lund", 71, "A-", None, 1),
    ("Henrik", "Dahl", 58, "B+", "Penicillin", 6),
    ("Maja", "Krogh", 45, "AB+", None, 4),
    ("Anders", "Bech", 39, "O+", None, 7),
    ("Laura", "Vinther", 29, "O-", "Pollen", 9),
    ("Erik", "Juhl", 82, "A+", None, 1),
]


def to_row(patient: dict, doctor_id: int) -> PatientRow:
    """Lav én patient-dict fra API'et om til en række til patient-tabellen."""
    # /add_patient i lektion 4 gemmer "bloodtype", patient.yml bruger "blood_type".
    blood_type = patient.get("blood_type") or patient.get("bloodtype")
    return (
        patient["first_name"],
        patient["last_name"],
        patient["age"],
        blood_type,
        clean_allergies(patient.get("allergies")),
        doctor_id,
    )


def api_patient_rows(patients: list[dict]) -> list[PatientRow]:
    """Giv API-patienterne en læge på skift: læge 1, 2, 3, ..."""
    return [to_row(patient, index % len(DOCTORS) + 1) for index, patient in enumerate(patients)]


def insert_hospitals(cursor: psycopg.Cursor) -> int:
    """Indsæt alle hospitaler. Returnér antallet af rækker."""
    sql = "INSERT INTO hospital (hospital_name, bed_count) VALUES (%s, %s)"
    cursor.executemany(sql, HOSPITALS)
    return cursor.rowcount


def insert_doctors(cursor: psycopg.Cursor) -> int:
    """Indsæt alle læger. Returnér antallet af rækker."""
    # TODO 3.2: brug insert_hospitals som model. Skriv en INSERT INTO doctor med de seks
    #           kolonner i samme rækkefølge som DoctorRow, og ét %s per kolonne.
    #           Kør cursor.executemany(sql, DOCTORS), og returnér cursor.rowcount.
    raise NotImplementedError("trin 3.2: insert_doctors")


def insert_patients(cursor: psycopg.Cursor, rows: list[PatientRow]) -> int:
    """Indsæt alle patienter. Returnér antallet af rækker."""
    # TODO 3.3: samme mønster med INSERT INTO patient og de seks kolonner i PatientRow.
    #           Bemærk: rækkerne kommer fra parameteren rows, ikke fra en konstant.
    raise NotImplementedError("trin 3.3: insert_patients")


def seed(patient_rows: list[PatientRow]) -> None:
    """Tøm tabellerne, og fyld dem igen i én transaction."""
    with get_connection() as conn, conn.cursor() as cursor:
        cursor.execute("TRUNCATE patient, doctor, hospital RESTART IDENTITY")
        logger.info("Hospitaler: %d", insert_hospitals(cursor))
        logger.info("Læger:      %d", insert_doctors(cursor))
        logger.info("Patienter:  %d", insert_patients(cursor, patient_rows))


def main() -> None:
    """Hent patienter fra API'et, og fyld alle tre tabeller."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    patient_rows = api_patient_rows(load_patients()) + EXTRA_PATIENTS
    try:
        seed(patient_rows)
    except psycopg.Error as error:
        logger.error("Databasefejl:\n%s", error)


if __name__ == "__main__":
    main()
