# Del 1 – Øvelse: database design og CRUD

**Mål:** flyt patienterne fra `patient.yml` (lektion 4) over i en PostgreSQL-tabel, og
create, read, update og delete dem fra Python, én ad gangen og mange på én gang.

**Når du er færdig, kan du:**

- designe et ER diagram for én tabel med en klar metode og omsætte det til `CREATE TABLE`
- bruge `NOT NULL`, `CHECK` og en genereret primary key
- køre `INSERT`, `SELECT`, `UPDATE` og `DELETE` fra Python med psycopg 3 og **t-strings**
- forklare, hvorfor t-strings og `%s` er sikre, og f-strings ikke er
- bruge `executemany()` til at indsætte, opdatere og slette mange rækker

**Sådan arbejder du:**

- Arbejd i mappen `del1_database_crud`. Deltrinene (1.1, 1.2 …) matcher `TODO`-numrene i koden.
- Efter hvert ✅ **Tjek** ved du, at den del virker. Gå ikke videre, før den gør.
- Sidder du fast? 1) Læs fejlbeskeden nedefra og op. 2) Læs hintet i `TODO`.
  3) Se på slidet for det trin. 4) Kig først derefter i `solution/`.

---

## Forberedelse (før undervisningen, ca. 60 min)

### P1. Installér PostgreSQL og pgAdmin (20 min)

1. Download PostgreSQL til Windows fra <https://www.postgresql.org/download/windows/>.
2. Kør installeren. Behold standardporten **5432**.
3. Vælg et password til brugeren `postgres`, og **skriv det ned**.
4. Installér **pgAdmin 4 version 9.18**, hvis installeren ikke havde det med: <https://www.pgadmin.org/download/>.
5. Åbn pgAdmin, fold **Servers → PostgreSQL** ud, og log ind med dit password.

### P2. Opret databasen (2 min)

1. Højreklik på **Databases**, og vælg **Create → Database…**
2. Name: `sundhedsapp`, derefter **Save**.
3. ✅ `sundhedsapp` står nu under **Databases**.

### P3. Sæt Python op (5 min)

1. Tjek din Python-version med `python --version`. Den skal være **3.14** eller nyere (kræves til t-strings). (Hvis den er installeret med Anaconda, så brug disse kommandoer i PowerShell for at opdatere versionen:
   conda activate base
   conda install python=3.14)
2. Kør `uv sync` i en terminal i mappen `sundhedsapp_postgres`.
3. I VS Code: `Ctrl+Shift+P`, vælg **Python: Select Interpreter**, og vælg `.venv`-interpreteren.
4. Åbn `db.py`. Hvis dit password ikke er `postgres`, så ret det i `DATABASE_URL`.

### P4. Læs (30 min)

1. Læs [theory.md](theory.md), og besvar de seks spørgsmål under "Test dig selv".
2. Læs [er_design_guide.md](er_design_guide.md). Du skal bruge dens 7 trin i trin 1.

---

> 🏠 **Trin 1–3 er en del af forberedelsen.** Lav dem hjemme, så tiden i undervisningen går til Python (trin 4–7).

## Trin 1: Design ER diagrammet (8 min)

Følg de 7 trin i [er_design_guide.md](er_design_guide.md). Skriv dine svar på papir eller i en
tekstfil først, og **tegn** først bagefter.

1. **1.1 Indsaml:** åbn `sundhedsapp/del4 visualisering/patient.yml`, og skriv alle felter ned.
2. **1.2 Entities:** hvilken *ting* beskriver felterne? Navngiv tabellen (ental, små bogstaver).
3. **1.3 Attributes:** vælg `integer` eller `text` for hvert felt. Hvorfor?
4. **1.4 Primary key:** hvorfor ikke `first_name + last_name`? Tilføj et `patient_id`.
5. **1.5 Påkrævet:** hvilke kolonner er `NOT NULL`? Hvilken må være tom?
   💡 YAML'en bruger `false`, `'No'` og `Peanuts`. Hvilken *ene* værdi skal betyde "ingen allergier"?
6. **1.6 Regler:** skriv `CHECK`-reglerne for `age` og `blood_type` ned.
7. **1.7 Tegn:** i pgAdmin, højreklik på `sundhedsapp`, og vælg **ERD For Database**, derefter
   **Add table**. Tilføj kolonnerne, sæt **Not NULL?** og **Primary key?**, og sæt `patient_id` til
   **IDENTITY / ALWAYS** (se pgAdmin-afsnittet i guiden).
8. **1.8 Gem:** gem diagrammet som `patient.pgerd` i denne mappe.

✅ **Tjek:** dit diagram har 1 tabel, 6 kolonner, en PK på `patient_id`, og kun `allergies` er uden Not NULL.

## Trin 2: Opret tabellen i SQL (6 min)

1. **2.1** Klik på **Generate SQL** i ERD Tool, og se på den kode, den laver.
2. **2.2** Åbn [schema.sql](schema.sql). Tilføj de 5 manglende kolonner *én linje ad gangen*:
   `name  TYPE  NOT NULL,`. Husk: **intet komma efter den sidste kolonne**.
3. **2.3** Tilføj de to `CHECK`-regler fra 1.6 (pgAdmin genererer dem ikke).
4. **2.4** I pgAdmin, højreklik på `sundhedsapp`, vælg **Query Tool**, indsæt din `schema.sql`, og tryk **F5**.
5. **2.5** I Object Explorer, fold `sundhedsapp → Schemas → public → Tables` ud.
   Højreklik, og vælg **Refresh**. `patient` skulle være der.
6. **2.6** Test dine regler i Query Tool. Det **første skal virke, de næste to skal fejle**:

```sql
INSERT INTO patient (first_name, last_name, age, blood_type)
VALUES ('Test', 'Testesen', 30, 'O+');

INSERT INTO patient (first_name, last_name, age, blood_type)
VALUES ('Bad', 'Age', -5, 'O+');

INSERT INTO patient (first_name, last_name, age, blood_type)
VALUES ('Bad', 'Blood', 30, 'Z');
```

7. **2.7** Kør `SELECT * FROM patient;`

✅ **Tjek:** én række, `patient_id = 1`, og `allergies` viser `[null]`.
Hvis et forkert `INSERT` **ikke** fejlede, mangler din `CHECK`: ret `schema.sql`, og kør den igen.

## Trin 3: Forbind fra Python (2 min)

1. **3.1** Kør:
   ```bash
   uv run db.py
   ```
2. ✅ **Tjek:** `Forbundet! Server: PostgreSQL 17...` (eller 18).

| Fejlen indeholder | Løsning |
|---|---|
| `password authentication failed` | forkert password i `DATABASE_URL` i `db.py` |
| `database "sundhedsapp" does not exist` | lav P2 igen |
| `Connection refused` | PostgreSQL-servicen kører ikke: start den i Windows **Services** |
| `No module named 'psycopg'` | kør `uv sync`, og brug `uv run` |

## Trin 4: Create og read med t-strings (10 min)

1. **4.1 Prøv t-strings i Python-shellen.** Kør `uv run python`, og skriv:
   ```python
   >>> name = "Holm"
   >>> f"WHERE last_name = {name}"
   >>> template = t"WHERE last_name = {name}"
   >>> template
   >>> template.strings
   >>> template.values
   >>> from psycopg import sql
   >>> sql.as_string(t"WHERE last_name = {name}")
   ```
   💡 Hvad er forskellen? f-stringen er almindelig tekst. t-stringen holder tekst og værdi
   **adskilt**, og derfor kan psycopg sende værdien sikkert. Skriv `exit()`, når du er færdig.
2. **4.2** Åbn [crud.py](crud.py). Gør `VALUES (...)`-linjen færdig i `create_patient`:
   `{first_name}, {last_name}, ...` i **samme rækkefølge** som kolonnelisten.
3. **4.3** Kør query med `conn.execute(query)` og `.fetchone()`, og returnér `row[0]`.
4. **4.4** Kør `uv run crud.py`. ✅ Du får `NotImplementedError: trin 4.5`, hvilket betyder, at 4.2–4.3 virker.
5. **4.5** Skriv `read_patient`: `t"SELECT * FROM patient WHERE patient_id = {patient_id}"` og `.fetchone()`.
6. **4.6** Kør `uv run crud.py`. ✅ Du ser noget i stil med
   `Oprettede patient 5: (5, 'Anna', 'Jensen', 45, 'AB+', 'Penicillin')` og derefter `NotImplementedError: trin 5.1`.

💡 Hvorfor er Annas id ikke 2? De to fejlede `INSERT`s i trin 2.6 brugte også et nummer, og
kørslen i 4.4 oprettede allerede én Anna. `IDENTITY` genbruger aldrig et nummer, og det er helt fint.

## Trin 5: Update og delete (5 min)

1. **5.1** Skriv `update_patient_age` med en t-string `UPDATE ... SET age = {age} WHERE patient_id = {patient_id}`.
   Gem cursoren: `cursor = conn.execute(...)`, og `return cursor.rowcount == 1` efter `with`.
2. **5.2** Skriv `delete_patient` på samme måde med `DELETE FROM patient WHERE ...`.
3. **5.3** Kør `uv run crud.py`.
4. **5.4** I pgAdmin, højreklik på `patient`, og vælg **View/Edit Data → All Rows**.

✅ **Tjek:** outputtet viser Anna med alder 45, derefter 46, og derefter `None` efter delete. pgAdmin
viser din testpatient fra trin 2 plus de Annaer, der blev oprettet i de halvfærdige kørsler i 4.4 og 4.6.
Kørslen i 5.3 slettede sin egen Anna. (Trin 7 tømmer tabellen, så de ekstra rækker gør ingen skade.)

⚠️ Tænk over det: hvad ville `t"DELETE FROM patient"` uden `WHERE` gøre?

## Trin 6: Lad databasen sige nej (3 min)

1. **6.1** I `main()`, kald `create_patient("Test", "Person", 30, "X+")`.
2. **6.2** Pak det ind i `try:` / `except CheckViolation as error:`, og log
   `error.diag.message_primary` med `logger.warning(...)`.
3. **6.3** Kør `uv run crud.py`.

✅ **Tjek:** `Afvist af databasen: new row for relation "patient" violates check constraint ...`
og programmet kører videre til "Alle patienter:".

💡 Diskutér med din sidemand: i lektion 4 accepterede API'et enhver blodtype. Hvor skal denne
regel ligge: i API'et, i databasen eller begge steder?

## Trin 7: Mange rækker med `executemany()` (12 min)

1. **7.1** Start appen fra lektion 4 i en **anden terminal**:
   ```bash
   cd "sundhedsapp/del4 visualisering"
   flask run
   ```
2. **7.2** Åbn <http://127.0.0.1:5000/docs>. Prøv **POST /token/{id}** med id `1`, kopiér token, og
   klik på **Authorize**. Prøv derefter **GET /health_data**. Det er de data, du skal importere.
3. **7.3** Åbn [bulk.py](bulk.py), og **læs** `get_token()`, `clean_allergies()`, `to_row()` og
   `insert_patients()`. De er færdige. Hvorfor bruger `insert_patients` `%s` og ikke en t-string?
   (Teoriafsnit 11.)
4. **7.4** Lav `headers`-dict'en med token i `fetch_patients`.
5. **7.5** Send `GET`-requesten, kald `raise_for_status()`, og returnér `response.json()["patients"]["id"]`.
6. **7.6** Kør `uv run bulk.py`. ✅ `Indsatte 4 patienter` og en liste, derefter `NotImplementedError: trin 7.7`.
7. **7.7** Skriv `update_ages`: kopiér `insert_patients`, og ændr SQL'en til `UPDATE`.
8. **7.8** Skriv `delete_patients`: lav først `[3, 4]` om til `[(3,), (4,)]` med en list comprehension.
9. **7.9** Kør `uv run bulk.py` igen.

✅ **Tjek:** 4 patienter bliver indsat, Kevin bliver 35 og Lone 67, og patient 3 og 4 bliver slettet.
Bekræft i pgAdmin (**View/Edit Data → All Rows**, tryk **F5** for at opdatere).

💡 Se på outputtet under "Efter insert": hvad skete der med `allergies: false` og `allergies: 'No'`?
Hvilken funktion gjorde det?

---

## Ekstra (hvis du har tid, eller hjemme)

1. **SQL injection:** skriv `find_by_last_name(name)` i `crud.py` med en t-string. Kald den med
   `"Holm"` og med `"x' OR '1'='1"`. Lav derefter (i en kopi!) en f-string-version, og prøv samme
   input. Hvad kommer der tilbage fra hver?
2. **Identifiers med `:i`:** skriv `read_patients_sorted(column)`, der kører
   `t"SELECT * FROM patient ORDER BY {column:i}"`. Hvorfor skal du først tjekke `column` mod en
   allow-list af kolonnenavne? Hvad sker der med `{column}` uden `:i`?
3. **Datakvalitet:** patient 4 har `last_name: holm` med små bogstaver. Ret det i `to_row()`,
   så alle navne starter med stort bogstav.
4. **One-to-many:** en patient kan have flere allergier. Brug trin 7 i ER-guiden: tegn en
   `allergy`-tabel i dit ERD med en foreign key til `patient`. (Vi bygger relationships for alvor i del 2.)
5. **Transactions:** i `insert_patients`, tilføj en række med blodtype `"Z"` sidst i listen.
   Hvor mange patienter er der i tabellen bagefter? Hvorfor?

## Refleksion

Skriv 2–3 sætninger i dine egne noter:

- Hvad kan databasen, som `patient.yml` ikke kunne?
- Hvornår ville du bruge `conn.execute(t"...")`, og hvornår `cursor.executemany("... %s ...", rows)`?
- Hvilket af de 7 ER design-trin var sværest, og hvorfor?

## Læs mere

Se linklisten nederst i [theory.md](theory.md#læs-mere).
