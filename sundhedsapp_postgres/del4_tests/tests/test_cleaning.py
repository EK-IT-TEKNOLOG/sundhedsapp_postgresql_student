"""Del 4, trin 1-2: dine første tests, af rene funktioner i cleaning.py.

Kør kun denne fil, med et navn per test (-v = verbose):

    uv run pytest tests/test_cleaning.py -v
"""

import pytest

from cleaning import clean_allergies, clean_blood_type, clean_name

# --- Trin 1: én test = én funktion, der starter med test_ og bruger assert -------------


def test_clean_name_capitalizes() -> None:
    assert clean_name("holm") == "Holm"


def test_clean_name_strips_spaces() -> None:
    # TODO 1.3: assert, at clean_name("  kevin  ") giver "Kevin". Brug testen ovenfor som model.
    raise NotImplementedError("trin 1.3")


def test_clean_name_keeps_hyphen() -> None:
    # TODO 1.4: "anne-marie" skal blive til "Anne-Marie".
    raise NotImplementedError("trin 1.4")


# --- Trin 2: parametrize og pytest.raises -------------------------------------------


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (False, None),
        ("No", None),
        # TODO 2.2: tilføj fem rækker mere: "no", "" og None skal give None,
        #           "Peanuts" skal give "Peanuts", og " Pollen " skal give "Pollen".
    ],
)
def test_clean_allergies(value: str | bool | None, expected: str | None) -> None:
    assert clean_allergies(value) == expected


def test_clean_blood_type_normalizes() -> None:
    # TODO 2.3: " ab+ " skal blive til "AB+".
    raise NotImplementedError("trin 2.3")


def test_clean_blood_type_rejects_unknown() -> None:
    # TODO 2.4: testen skal bestå, når clean_blood_type("X+") kaster en ValueError:
    #               with pytest.raises(ValueError):
    #                   clean_blood_type("X+")
    raise NotImplementedError("trin 2.4")


def test_clean_name_rejects_empty() -> None:
    # TODO 2.5: clean_name("   ") skal kaste ValueError, og beskeden skal indeholde "tom".
    #           Brug pytest.raises(ValueError, match="tom").
    raise NotImplementedError("trin 2.5")
