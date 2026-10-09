# Sundhedsapp – PostgreSQL (lektion 5)

I lektion 4 byggede du sundhedsappen: et Flask API, der gemmer patienter i
`patient.yml` og beskytter `/health_data` med et bearer token.
I denne lektion flytter vi patienterne fra en YAML-fil over i en rigtig database: **PostgreSQL**.

| Del | Mappe | Emne |
|------|--------|-------|
| 1 | [del1_database_crud](del1_database_crud/) | Database design, ER diagram, CRUD, `executemany()` |
| 2 | [del2_hospital](del2_hospital/) | Hospitaler og læger, `GROUP BY`, `HAVING`, stored procedures |
| 3 | [del3_login](del3_login/) | Login system med Flask og role-based access control |
| 4 | [del4_tests](del4_tests/) | pytest, pytest-postgresql, login fixtures |

Hver del: 45 minutter i undervisningen (teori + øvelse). Læs teorien før undervisningen.

## Værktøjer

- Python 3.14
- PostgreSQL server (17 eller nyere)
- pgAdmin 4 version 9.18
- psycopg 3.3 eller nyere (kræves til t-string queries)
- VS Code
- uv

## Setup (én gang)

Kør fra denne mappe:

```bash
uv sync
```

Det opretter et `.venv` med `psycopg` og `requests` installeret, til del 3 `apiflask` og `joserfc`, og til del 4 `pytest` og `pytest-postgresql` (dev).
Vælg `.venv`-interpreteren i VS Code (`Ctrl+Shift+P` → *Python: Select Interpreter*).
