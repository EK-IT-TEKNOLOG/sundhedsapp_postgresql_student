"""Del 4: små funktioner, der renser patientdata, før de gemmes (færdig).

Funktionerne er "rene": samme input giver altid samme output, og de rører hverken
databasen, netværket eller filer. Derfor er de de nemmeste at teste, og vi starter med dem.
"""

NO_ALLERGY = {"", "no", "none", "false"}
BLOOD_TYPES = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}


def clean_allergies(value: str | bool | None) -> str | None:
    """YAML-filen blander False, 'No' og rigtige allergier. Gem 'ingen' som None."""
    if value is None or value is False or str(value).strip().lower() in NO_ALLERGY:
        return None
    return str(value).strip()


def clean_name(name: str) -> str:
    """'  holm ' -> 'Holm' og 'anne-marie' -> 'Anne-Marie'. Et tomt navn giver ValueError."""
    cleaned = name.strip()
    if not cleaned:
        raise ValueError("Navnet må ikke være tomt")
    return "-".join(part.capitalize() for part in cleaned.split("-"))


def clean_blood_type(value: str) -> str:
    """' ab+ ' -> 'AB+'. En ukendt blodtype giver ValueError."""
    blood_type = value.strip().upper()
    if blood_type not in BLOOD_TYPES:
        raise ValueError(f"Ukendt blodtype: {value!r}")
    return blood_type
