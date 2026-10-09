"""Del 3, trin 3 og 5: brugere i databasen.

Kør filen for at oprette testbrugerne med hashede passwords:

    uv run users.py
"""

import logging

import psycopg
from psycopg.rows import dict_row
from werkzeug.security import generate_password_hash

from db import get_connection

logger = logging.getLogger(__name__)

# (username, password, role_name, doctor_id)
UserSeed = tuple[str, str, str, int | None]

# Kun til undervisning. Rigtige passwords står aldrig i koden.
TEST_USERS: list[UserSeed] = [
    ("admin", "admin-pass", "admin", None),
    ("mette", "mette-pass", "doctor", 1),   # Mette Sørensen
    ("jonas", "jonas-pass", "doctor", 2),   # Jonas Madsen
    ("nina", "nina-pass", "nurse", None),
]


def get_user_by_username(username: str) -> dict | None:
    """Find en bruger ud fra brugernavn, med password_hash, så login kan tjekke den."""
    query = t"""
        SELECT u.user_id, u.username, u.password_hash, u.doctor_id, r.role_name
        FROM app_user AS u
        JOIN role AS r ON r.role_id = u.role_id
        WHERE u.username = {username}
    """
    with get_connection() as conn, conn.cursor(row_factory=dict_row) as cursor:
        return cursor.execute(query).fetchone()


def get_user(user_id: int) -> dict | None:
    """Find en bruger ud fra id. Uden password_hash: den skal aldrig ud af serveren."""
    # TODO 5.1: kopiér get_user_by_username, og ret to ting:
    #           - fjern u.password_hash fra SELECT
    #           - WHERE u.user_id = {user_id}
    raise NotImplementedError("trin 5.1: get_user")


def create_users(users: list[UserSeed]) -> int:
    """Slet alle brugere, og opret dem igen med hashede passwords."""
    # Subqueryen slår role_id op ud fra rollens navn, så vi slipper for at huske tal.
    sql = """
        INSERT INTO app_user (username, password_hash, role_id, doctor_id)
        VALUES (%s, %s, (SELECT role_id FROM role WHERE role_name = %s), %s)
    """
    # TODO 3.2: lav rows med en list comprehension. Hver tuple i users er
    #           (username, password, role_name, doctor_id). Byt password ud med
    #           generate_password_hash(password), og behold resten i samme rækkefølge.
    rows = []
    with get_connection() as conn, conn.cursor() as cursor:
        cursor.execute("TRUNCATE app_user RESTART IDENTITY")
        cursor.executemany(sql, rows)
        return cursor.rowcount


def main() -> None:
    """Opret testbrugerne, og vis, hvad der faktisk står i databasen."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    try:
        logger.info("Oprettede %d brugere", create_users(TEST_USERS))
        logger.info("mette i databasen: %s", get_user_by_username("mette"))
        logger.info("get_user(2):       %s", get_user(2))
    except psycopg.Error as error:
        logger.error("Databasefejl:\n%s", error)


if __name__ == "__main__":
    main()
