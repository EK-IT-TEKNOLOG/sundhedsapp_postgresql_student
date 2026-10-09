"""Del 2, trin 7: kald en function og en procedure fra Python.

Kør procedures.sql i pgAdmin først, så de findes i databasen.
Hver kørsel giver Pædiatri en lønstigning. Kør seed.py igen for at starte forfra.

Udfyld TODOs i rækkefølge, og kør filen:

    uv run procedures.py
"""

import logging

import psycopg
from psycopg.errors import RaiseException

from db import get_connection

logger = logging.getLogger(__name__)


def doctors_by_speciality(speciality: str) -> list[tuple]:
    """Kald function'en: den returnerer rækker, så vi bruger SELECT."""
    # TODO 7.4: t"SELECT * FROM doctors_by_speciality({speciality})" og .fetchall()
    #           En function bruges præcis som en tabel i FROM.
    raise NotImplementedError("trin 7.4: doctors_by_speciality")


def raise_salary(speciality: str, percent: int) -> None:
    """Kald proceduren: den returnerer ingenting, så vi bruger CALL."""
    # TODO 7.5: t"CALL raise_salary({speciality}, {percent})"
    #           Der er ingen rækker at hente, så du skal ikke kalde fetch.
    raise NotImplementedError("trin 7.5: raise_salary")


def log_rows(title: str, rows: list[tuple]) -> None:
    """Log en liste af rækker under en overskrift."""
    logger.info(title)
    for row in rows:
        logger.info("  %s", row)


def main() -> None:
    """Vis lønningerne, giv en lønstigning, og se databasen sige nej."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    try:
        log_rows("Pædiatri før:", doctors_by_speciality("Pædiatri"))
        raise_salary("Pædiatri", 10)
        log_rows("Pædiatri efter 10 % lønstigning:", doctors_by_speciality("Pædiatri"))

        # TODO 7.6: kald raise_salary("Tandlæge", 10). Pak kaldet ind i
        #           try / except RaiseException as error:
        #           og log error.diag.message_primary med logger.warning(...)
    except psycopg.Error as error:
        logger.error("Databasefejl:\n%s", error)


if __name__ == "__main__":
    main()
