# Del 2: Hospitaler, læger og patienter

Udvid sundhedsappen fra én tabel til tre, forbind dem med foreign keys, og stil spørgsmål til data
med `JOIN`, `GROUP BY`, `HAVING` og stored procedures.

## Plan

| Hvornår | Hvad | Tid |
|---|---|---|
| Før undervisningen | Læs [theory.md](theory.md), og ret password i `db.py` | 35 min |
| Før undervisningen | [exercise.md](exercise.md) trin 1–3: ER diagram, `CREATE TABLE`, fyld tabellerne | 23 min |
| I undervisningen | Slides ([del2_theory.pptx](del2_theory.pptx)): opsummering og gennemgang af trin 4–7 | 10 min |
| I undervisningen | [exercise.md](exercise.md) trin 4–7: `JOIN`, `GROUP BY`, `HAVING`, stored procedures | 30 min |
| I undervisningen | Buffer eller ekstraopgaver | 5 min |

## Filer

| Fil | Hvad det er |
|---|---|
| [exercise.md](exercise.md) | Øvelsestrinene. **Start her** |
| [theory.md](theory.md) | Teori til at læse før undervisningen, med links til mere læsning |
| [del2_theory.pptx](del2_theory.pptx) | Slides: teori og hvordan du løser hvert trin |
| [db.py](db.py) | Connection helper (færdig). Skift password her |
| [api.py](api.py) | Henter patienter fra API'et i lektion 4 med bearer token (færdig) |
| [schema.sql](schema.sql) | Trin 2: tre tabeller med foreign keys, med TODOs |
| [seed.py](seed.py) | Trin 3: fyld tabellerne med `executemany()`, med TODOs |
| [queries.py](queries.py) | Trin 4–6: `JOIN`, `GROUP BY`, `HAVING`, med TODOs |
| [procedures.sql](procedures.sql) | Trin 7: en function og en procedure, med TODO |
| [procedures.py](procedures.py) | Trin 7: kald dem fra Python, med TODOs |
| [solution/](solution/) | Løsninger. Kør dem med `uv run python -m solution.queries` |

## Står alene

Del 2 kræver ikke, at del 1 er færdig. `schema.sql` opretter alle tre tabeller forfra, og `seed.py`
fylder dem. Kører API'et fra lektion 4 ikke, bruger `seed.py` en kopi af `patient.yml`.
