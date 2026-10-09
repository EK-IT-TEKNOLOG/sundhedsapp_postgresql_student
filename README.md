# Sundhedsapp

Øvelsesmateriale til Python-undervisningen, hvor de studerende bygger en lille sundhedsapp trin for trin:
først et Flask API, der gemmer patienter i en YAML-fil (lektion 4), og derefter samme app med en rigtig
**PostgreSQL**-database, login og tests (lektion 5).

## Indhold

| Mappe | Lektion | Emne |
|---|---|---|
| [sundhedsapp/](sundhedsapp/) | 4 | YAML, Flask API, bearer tokens, visualisering |
| [sundhedsapp_postgres/](sundhedsapp_postgres/) | 5 | PostgreSQL, SQL, login med roller, pytest |

### Lektion 4: `sundhedsapp/`

Hver del bygger videre på den forrige. `del4 visualisering` er den færdige app, som lektion 5 bruger.

| Del | Mappe | Emne |
|---|---|---|
| 1 | [del1 yaml](<sundhedsapp/del1 yaml/>) | Læs og skriv patienter i `patient.yml` |
| 2 | [del2 API](<sundhedsapp/del2 API/>) | Tilføj og hent patienter via et APIFlask API |
| 3 | [del3 token](<sundhedsapp/del3 token/>) | Beskyt API'et med JWT bearer tokens |
| 4 | [del4 visualisering](<sundhedsapp/del4 visualisering/>) | Plot patientdata med pandas og Plotly |

### Lektion 5: `sundhedsapp_postgres/`

Fire dele á 45 minutter med teori, slides, øvelser og løsninger. Hver del kan køres for sig.
Se [sundhedsapp_postgres/README.md](sundhedsapp_postgres/README.md) for detaljer.

| Del | Mappe | Emne |
|---|---|---|
| 1 | [del1_database_crud](sundhedsapp_postgres/del1_database_crud/) | ER diagram, `CREATE TABLE`, CRUD, `executemany()` |
| 2 | [del2_hospital](sundhedsapp_postgres/del2_hospital/) | Hospitaler og læger, `JOIN`, `GROUP BY`, `HAVING`, stored procedures |
| 3 | [del3_login](sundhedsapp_postgres/del3_login/) | Login med Flask, hashede passwords, role-based access control |
| 4 | [del4_tests](sundhedsapp_postgres/del4_tests/) | pytest, pytest-postgresql, login-fixtures |

Hver del-mappe indeholder:

- `README.md`: plan og filoversigt
- `exercise.md`: øvelsestrinene. **Start her**
- `theory.md` og `delX_theory.pptx`: teori og slides
- kodefiler med `TODO`s, som de studerende udfylder
- `solution/`: løsningerne

## Værktøjer

- [Python 3.14](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/) til pakker og virtuelle miljøer, se [UV_GUIDE.md](UV_GUIDE.md)
- [PostgreSQL](https://www.postgresql.org/download/) 17 eller nyere
- [pgAdmin 4](https://www.pgadmin.org/) 9.18
- [VS Code](https://code.visualstudio.com/)

## Kom i gang

```bash
git clone <repo-url>
cd <repo-mappe>/sundhedsapp_postgres
uv sync
```

`uv sync` opretter `.venv` og installerer alt fra `pyproject.toml` (psycopg, apiflask, joserfc, requests,
pytest og pytest-postgresql). Vælg derefter `.venv` som interpreter i VS Code
(`Ctrl+Shift+P` → *Python: Select Interpreter*).

**Database:** koden forbinder som standard til
`postgresql://postgres:postgres@localhost:5432/sundhedsapp`. Har du et andet password, så ret det i
`db.py` i den del, du arbejder på, eller sæt environment variablen `DATABASE_URL`:

```powershell
$env:DATABASE_URL = "postgresql://postgres:<dit-password>@localhost:5432/sundhedsapp"
```

Gå derefter til [del 1](sundhedsapp_postgres/del1_database_crud/exercise.md).

### Kør appen fra lektion 4

Del 1 og 2 i lektion 5 kan hente patienter fra API'et i lektion 4. Lektion 4 har ikke sin egen
`pyproject.toml`, så pakkerne gives med `--with`:

```bash
cd "sundhedsapp/del4 visualisering"
uv run --with apiflask --with authlib --with pyyaml --with pandas --with plotly flask run
```

Åbn <http://127.0.0.1:5000/docs> for at se API'et. Kører det ikke, bruger lektion 5 en kopi af
patientdataene, så øvelserne også virker alene.

### Kør testene

```bash
cd sundhedsapp_postgres/del4_tests
uv run pytest                  # de studerendes tests (fejler, indtil TODOs er løst)
uv run pytest solution/tests   # løsningerne
```

## Til underviseren: byg slides

Slides bygges med `python-pptx` ud fra EK-skabelonen i `sundhedsapp_postgres/slides/`.
Luk præsentationen i PowerPoint først, og kør fra `sundhedsapp_postgres`:

```bash
uv run --with python-pptx slides/build_del1.py
```

## Licens

Koden i `sundhedsapp/` er udgivet under GNU GPL v3 (se `LICENSE` i hver del-mappe).
