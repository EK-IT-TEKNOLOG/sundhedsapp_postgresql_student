# Del 1: Database design og CRUD

Flyt patienterne fra `patient.yml` (lektion 4) over i PostgreSQL, og create, read,
update og delete dem derefter fra Python med psycopg 3 og t-strings.

## Plan

| Hvornår | Hvad | Tid |
|---|---|---|
| Før undervisningen | Installér og sæt op (P1–P3), læs [theory.md](theory.md) og [er_design_guide.md](er_design_guide.md) (P4) | 60 min |
| Før undervisningen | [exercise.md](exercise.md) trin 1–3: ER diagram, `CREATE TABLE`, forbind | 16 min |
| I undervisningen | Slides ([del1_theory.pptx](del1_theory.pptx)): opsummering og gennemgang af trin 4–7 | 10 min |
| I undervisningen | [exercise.md](exercise.md) trin 4–7: CRUD med t-strings, `executemany()` | 30 min |
| I undervisningen | Buffer eller ekstraopgaver | 5 min |

## Filer

| Fil | Hvad det er |
|---|---|
| [exercise.md](exercise.md) | Øvelsestrinene. **Start her** |
| [theory.md](theory.md) | Teori til at læse før undervisningen, med links til mere læsning |
| [er_design_guide.md](er_design_guide.md) | 7-trins-metoden til at designe et ER diagram, plus pgAdmin ERD Tool |
| [del1_theory.pptx](del1_theory.pptx) | Slides: teori og hvordan du løser hvert trin |
| [db.py](db.py) | Connection helper (færdig). Skift password her |
| [schema.sql](schema.sql) | Trin 2: `CREATE TABLE` med TODOs |
| [crud.py](crud.py) | Trin 4–6: én patient ad gangen med t-strings, med TODOs |
| [bulk.py](bulk.py) | Trin 7: `executemany()` og import fra API'et, med TODOs |
| [solution/](solution/) | Løsninger. Kør dem med `uv run python -m solution.crud` |

## Krav

Python **3.14** og psycopg **3.3** eller nyere. t-strings findes ikke i ældre versioner.
