"""Hent patienterne fra API'et fra lektion 4 med et bearer token (færdig, samme som del 1).

Start appen fra lektion 4 først (sundhedsapp/del4 visualisering: flask run).
Kører API'et ikke, bruger load_patients() en kopi af patient.yml, så del 2 også virker alene.
"""

import logging

import requests

logger = logging.getLogger(__name__)

API_URL = "http://127.0.0.1:5000"
NO_ALLERGY = {"", "no", "none", "false"}

# Samme fire patienter som i patient.yml fra lektion 4.
LESSON_4_PATIENTS = [
    {"first_name": "Kevin", "last_name": "Holm", "age": 34, "blood_type": "O+", "allergies": False},
    {"first_name": "Lone", "last_name": "Kellerman", "age": 66, "blood_type": "A+", "allergies": "Peanuts"},
    {"first_name": "Lars", "last_name": "Larsson", "age": 27, "blood_type": "B-", "allergies": "Strawberry"},
    {"first_name": "Mel", "last_name": "holm", "age": 34, "blood_type": "O-", "allergies": "No"},
]


def get_token(user_id: int = 1) -> str:
    """Bed API'et om et token. API'et returnerer det som 'Bearer <token>'."""
    response = requests.post(f"{API_URL}/token/{user_id}", timeout=5)
    response.raise_for_status()
    return response.json()["token"]


def fetch_patients(token: str) -> list[dict]:
    """Hent alle patienter fra det beskyttede /health_data endpoint."""
    headers = {"Authorization": token}
    response = requests.get(f"{API_URL}/health_data", headers=headers, timeout=5)
    response.raise_for_status()
    return list(response.json()["patients"]["id"].values())


def load_patients() -> list[dict]:
    """Hent patienterne fra API'et, eller brug kopien, hvis API'et ikke svarer."""
    try:
        return fetch_patients(get_token())
    except requests.RequestException as error:
        logger.warning("API'et svarer ikke, så jeg bruger kopien af patient.yml.\n  (%s)", error)
        return LESSON_4_PATIENTS


def clean_allergies(value: str | bool | None) -> str | None:
    """YAML-filen blander False, 'No' og rigtige allergier. Gem 'ingen' som NULL."""
    if value is None or value is False or str(value).strip().lower() in NO_ALLERGY:
        return None
    return str(value)
