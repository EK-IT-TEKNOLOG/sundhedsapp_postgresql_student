"""Del 2, trin 4-6: JOIN, GROUP BY og HAVING.

Skriv hver query i pgAdmins Query Tool først, så du kan se resultatet med det samme.
Kopiér den derefter herind. Queries uden værdier er almindelige strenge. Queries med en
værdi er t-strings, så psycopg sender værdien som en parameter.

Udfyld TODOs i rækkefølge. Kør filen efter hver funktion:

    uv run queries.py
"""

import logging

import psycopg

from db import get_connection

logger = logging.getLogger(__name__)


# --- Trin 4: JOIN ------------------------------------------------------------------


def doctors_with_hospital() -> list[tuple]:
    """Hver læge med navnet på sit hospital. Færdig: brug den som model."""
    sql = """
        SELECT d.doctor_name, d.speciality, h.hospital_name
        FROM doctor AS d
        JOIN hospital AS h ON h.hospital_id = d.hospital_id
        ORDER BY h.hospital_name, d.doctor_name
    """
    with get_connection() as conn:
        return conn.execute(sql).fetchall()


def patients_at_hospital(hospital_id: int) -> list[tuple]:
    """Alle patienter, hvis læge arbejder på hospitalet, med lægens navn."""
    # TODO 4.2: SELECT p.first_name, p.last_name, d.doctor_name
    #           FROM patient AS p JOIN doctor AS d ON ... (hvilke kolonner hænger sammen?)
    #           WHERE d.hospital_id = {hospital_id}, ORDER BY p.last_name
    #           Skriv den som en t-string, og returnér .fetchall().
    raise NotImplementedError("trin 4.2: patients_at_hospital")


# --- Trin 5: GROUP BY --------------------------------------------------------------


def doctors_per_hospital() -> list[tuple]:
    """Antal læger per hospital. Hospitaler uden læger skal også med (med 0)."""
    # TODO 5.3: SELECT h.hospital_name, COUNT(d.doctor_id) AS doctors
    #           FROM hospital AS h LEFT JOIN doctor AS d ON ...
    #           GROUP BY h.hospital_name, ORDER BY doctors DESC, h.hospital_name
    raise NotImplementedError("trin 5.3: doctors_per_hospital")


def salary_by_speciality() -> list[tuple]:
    """Antal læger, gennemsnitsløn og højeste løn per speciale."""
    # TODO 5.5: fire kolonner: speciality, COUNT(*), AVG(salary)::integer, MAX(salary)
    #           GROUP BY speciality, ORDER BY speciality
    #           (::integer runder gennemsnittet til et heltal)
    raise NotImplementedError("trin 5.5: salary_by_speciality")


# --- Trin 6: HAVING ----------------------------------------------------------------


def specialities_with_min_doctors(min_doctors: int) -> list[tuple]:
    """Specialer med mindst min_doctors læger."""
    # TODO 6.1: SELECT speciality, COUNT(*) AS doctors FROM doctor
    #           GROUP BY speciality HAVING COUNT(*) >= {min_doctors} ORDER BY doctors DESC
    #           Det er en t-string, fordi min_doctors er en værdi.
    raise NotImplementedError("trin 6.1: specialities_with_min_doctors")


def well_paid_specialities(min_avg_salary: int) -> list[tuple]:
    """Specialer, hvor gennemsnitslønnen er over min_avg_salary."""
    # TODO 6.4: speciality og AVG(salary)::integer AS avg_salary,
    #           kun grupper, hvor AVG(salary) > {min_avg_salary}, ORDER BY avg_salary DESC
    raise NotImplementedError("trin 6.4: well_paid_specialities")


def log_rows(title: str, rows: list[tuple]) -> None:
    """Log en liste af rækker under en overskrift."""
    logger.info(title)
    for row in rows:
        logger.info("  %s", row)


def main() -> None:
    """Kør alle queries i rækkefølge og log resultaterne."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    try:
        log_rows("Trin 4.1 Læger og deres hospital:", doctors_with_hospital())
        log_rows("Trin 4.3 Patienter på Rigshospitalet (id 1):", patients_at_hospital(1))
        log_rows("Trin 5.3 Læger per hospital:", doctors_per_hospital())
        log_rows("Trin 5.5 Løn per speciale:", salary_by_speciality())
        log_rows("Trin 6.1 Specialer med mindst 3 læger:", specialities_with_min_doctors(3))
        log_rows("Trin 6.4 Specialer med gennemsnitsløn over 65000:", well_paid_specialities(65000))
    except psycopg.Error as error:
        logger.error("Databasefejl:\n%s", error)


if __name__ == "__main__":
    main()
