# Del 4: Tests med pytest

Skriv automatiske tests til sundhedsappen: rene funktioner, databasefunktioner mod en frisk
testdatabase (pytest-postgresql) og login og adgangsregler med en login-fixture.

## Plan

| Hvornår | Hvad | Tid |
|---|---|---|
| Før undervisningen | `uv sync`, ret password i `db.py`, læs [theory.md](theory.md) | 35 min |
| Før undervisningen | [exercise.md](exercise.md) trin 1–2: første tests, `parametrize`, `pytest.raises` | 20 min |
| I undervisningen | Slides ([del4_theory.pptx](del4_theory.pptx)): opsummering og gennemgang af trin 3–6 | 10 min |
| I undervisningen | [exercise.md](exercise.md) trin 3–6: `monkeypatch`, pytest-postgresql, login-fixture, adgangsregler | 30 min |
| I undervisningen | Buffer eller ekstraopgaver | 5 min |

## Filer

| Fil | Hvad det er |
|---|---|
| [exercise.md](exercise.md) | Øvelsestrinene. **Start her** |
| [theory.md](theory.md) | Teori til at læse før undervisningen, med links til mere læsning |
| [del4_theory.pptx](del4_theory.pptx) | Slides: teori og hvordan du løser hvert trin |
| [pytest.ini](pytest.ini) | pytest-indstillinger: hvor testene ligger |
| [cleaning.py](cleaning.py) | Trin 1–2: små rene funktioner at teste (færdig) |
| `db.py`, `users.py`, `patients.py`, `auth.py`, `app.py` | App'en fra del 3 (færdig). Skift password i `db.py` |
| `schema.sql`, `data.sql` | Tabeller og data, som testdatabasen bygges af (færdig) |
| [tests/conftest.py](tests/conftest.py) | Fixtures: testdatabase, Flask client og login, med TODO |
| [tests/](tests/) | Dine tests, med TODOs: `test_cleaning`, `test_tokens`, `test_database`, `test_login`, `test_access` |
| [solution/tests/](solution/tests/) | Løsninger. Kør dem med `uv run pytest solution/tests` |

## Din database er sikker

Testene bruger din PostgreSQL-server og password fra `db.py`, men laver deres egne databaser
(`sundhedsapp_test…`) og sletter dem igen. Din `sundhedsapp`-database bliver ikke rørt.

## Står alene

Del 4 kræver ikke, at del 1–3 er færdige. Den har sin egen færdige kopi af app'en fra del 3.
