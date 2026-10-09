"""Database connection helper, som alle scripts i del 1 deler.

Kør filen direkte for at tjekke, at Python kan nå PostgreSQL:

    uv run db.py
"""

import logging
import os

import psycopg

logger = logging.getLogger(__name__)

# Skift password her, eller sæt environment variablen DATABASE_URL.
# Format: postgresql://<user>:<password>@<host>:<port>/<database>
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/sundhedsapp",
)


def get_connection() -> psycopg.Connection:
    """Åbn en ny connection til sundhedsapp-databasen."""
    return psycopg.connect(DATABASE_URL)


def main() -> None:
    """Tjek connection ved at spørge serveren om dens version."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    try:
        with get_connection() as conn:
            version = conn.execute("SELECT version()").fetchone()[0]
    except psycopg.OperationalError as error:
        logger.error("Kunne ikke forbinde til PostgreSQL:\n%s", error)
        return
    logger.info("Forbundet! Server: %s", version)


if __name__ == "__main__":
    main()
