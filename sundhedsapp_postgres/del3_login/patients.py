"""Del 3, trin 6: patient-queries, som API'et bruger.

dict_row giver rækker som dicts: {"first_name": "Kevin", ...}. Flask kan sende dem direkte som JSON.
"""

from psycopg.rows import dict_row

from db import get_connection


def all_patients() -> list[dict]:
    """Alle patienter med navnet på deres læge."""
    sql = """
        SELECT p.patient_id, p.first_name, p.last_name, p.age, p.blood_type,
               p.allergies, d.doctor_name
        FROM patient AS p
        JOIN doctor AS d ON d.doctor_id = p.doctor_id
        ORDER BY p.patient_id
    """
    with get_connection() as conn, conn.cursor(row_factory=dict_row) as cursor:
        return cursor.execute(sql).fetchall()


def patients_of_doctor(doctor_id: int) -> list[dict]:
    """Kun de patienter, der hører til én læge."""
    # TODO 6.3: SELECT patient_id, first_name, last_name, age, blood_type, allergies
    #           FROM patient WHERE doctor_id = {doctor_id} ORDER BY patient_id
    #           Brug en t-string og samme with-linje som all_patients, og returnér .fetchall().
    raise NotImplementedError("trin 6.3: patients_of_doctor")


def delete_patient(patient_id: int) -> bool:
    """Slet en patient. Returnér True, hvis en række blev slettet."""
    with get_connection() as conn:
        cursor = conn.execute(t"DELETE FROM patient WHERE patient_id = {patient_id}")
    return cursor.rowcount == 1
