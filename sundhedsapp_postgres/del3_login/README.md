# Del 3: Login med Flask og role-based access control

Giv sundhedsappen et rigtigt login: brugere og roller i PostgreSQL, hashede passwords, JWT bearer
tokens med udløbstid og adgangsregler per rolle.

## Plan

| Hvornår | Hvad | Tid |
|---|---|---|
| Før undervisningen | `uv sync`, læs [theory.md](theory.md), og ret password i `db.py` | 35 min |
| Før undervisningen | [exercise.md](exercise.md) trin 1–3: ER diagram, tabeller, hashede brugere | 21 min |
| I undervisningen | Slides ([del3_theory.pptx](del3_theory.pptx)): opsummering og gennemgang af trin 4–7 | 10 min |
| I undervisningen | [exercise.md](exercise.md) trin 4–7: login, tokens, roller, test af reglerne | 30 min |
| I undervisningen | Buffer eller ekstraopgaver | 5 min |

## Filer

| Fil | Hvad det er |
|---|---|
| [exercise.md](exercise.md) | Øvelsestrinene. **Start her** |
| [theory.md](theory.md) | Teori til at læse før undervisningen, med links til mere læsning |
| [del3_theory.pptx](del3_theory.pptx) | Slides: teori og hvordan du løser hvert trin |
| [db.py](db.py) | Connection helper (færdig). Skift password her |
| [schema.sql](schema.sql) | Trin 2: tabellerne fra del 2 plus `role` og `app_user`, med TODOs |
| [data.sql](data.sql) | Trin 2: hospitaler, læger og patienter (færdig) |
| [users.py](users.py) | Trin 3 og 5: opret brugere med hashede passwords, find brugere, med TODOs |
| [auth.py](auth.py) | Trin 4–6: login, tokens og roller, med TODOs |
| [patients.py](patients.py) | Trin 6: patient-queries med `dict_row`, med TODO |
| [app.py](app.py) | Trin 4–6: Flask API'et, med TODOs |
| [client.py](client.py) | Trin 7: tester alle adgangsregler udefra, med TODOs |
| [solution/](solution/) | Løsninger. Start med `uv run flask --app solution.app run --port 5001` |

## Nye pakker

Del 3 bruger `apiflask` (som i lektion 4) og `joserfc` (efterfølgeren til `authlib.jose`).
Kør `uv sync` i mappen `sundhedsapp_postgres` for at installere dem.

## Står alene

Del 3 kræver ikke, at del 1 og 2 er færdige. `schema.sql` opretter alle fem tabeller, og `data.sql`
fylder hospitaler, læger og patienter.
