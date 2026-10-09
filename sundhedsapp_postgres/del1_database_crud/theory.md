# Del 1 – Teori: database design og CRUD

Læs dette før undervisningen (ca. 45 minutter inklusive ER-guiden). Slides'ene `del1_theory.pptx`
dækker de samme emner og viser, hvordan du løser hvert trin i øvelsen.

---

## 1. Hvorfor forlade YAML-filen?

I lektion 4 gjorde hver request dette: læs hele `patient.yml`, ændr en dict og skriv hele
filen tilbage. Det fungerer med 4 patienter. Det går i stykker, når:

- **To requests skriver samtidig**, så én ændring går tabt.
- **Data er forkert**: `allergies: false`, `'No'` og `Peanuts` er alle tilladt. `age: -5` er også tilladt.
- **Data vokser**: for at finde én patient skal du læse alle patienter.

En **relationel database** som PostgreSQL løser alle tre: den håndterer mange brugere på én gang,
den **håndhæver regler** for data, og den kan finde rækker hurtigt.

## 2. Tabeller, rækker og kolonner

| Ord | YAML (lektion 4) | PostgreSQL |
|---|---|---|
| Tabel (table) | `patients:` | `patient` |
| Række (row) | én patient-dict | én række |
| Kolonne (column) | en key som `age` | en kolonne med en **data type** |
| Primary key | dict key'en `1:` | `patient_id` |

Hver kolonne har en data type. Vi bruger tre:

| Type | Bruges til | Eksempel |
|---|---|---|
| `INTEGER` | heltal | `age`, `patient_id` |
| `TEXT` | strenge af vilkårlig længde | `first_name` |
| `NULL` | ikke en type, men "ingen værdi" | `allergies` for en patient uden allergier |

## 3. Primary key og constraints

En **primary key** identificerer præcis én række. Den skal være unik og aldrig `NULL`.

```sql
patient_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY
```

`GENERATED ALWAYS AS IDENTITY` betyder, at PostgreSQL vælger det næste nummer (1, 2, 3…). Du skriver
aldrig selv id'et. Det erstatter `len(new) + 1` fra lektion 4, som går i stykker, når en patient bliver slettet.

**Constraints** er regler, som databasen håndhæver. Hvis en regel brydes, fejler statementet:

| Constraint | Betydning |
|---|---|
| `NOT NULL` | en værdi er påkrævet |
| `CHECK (age BETWEEN 0 AND 150)` | værdien skal bestå en test |
| `CHECK (blood_type IN ('A+', 'A-', ...))` | kun værdier fra en liste er tilladt |

> Regler i databasen beskytter data, uanset hvilket program der skriver til den: dit API, pgAdmin eller
> en klassekammerats script.

## 4. ER diagram

Et **Entity–Relationship diagram** er en tegning af tabellerne, før du bygger dem.

- **Entity** er en ting, vi gemmer data om, og den bliver til en tabel (`patient`).
- **Attribute** er en oplysning om entity'en, og den bliver til en kolonne (`age`).
- **Relationship** er, hvordan entities hænger sammen (del 2: en læge *arbejder på* et hospital).

Metoden, vi bruger, har 7 trin:

1. Indsaml de data, du skal gemme
2. Find entities
3. Find attributes, og vælg en data type til hver
4. Vælg primary key
5. Beslut, hvad der er påkrævet (`NULL` / `NOT NULL`)
6. Tilføj regler (`CHECK`)
7. Tjek designet: én værdi per celle, intet gemt to gange

📖 **Læs [er_design_guide.md](er_design_guide.md)**. Den gennemgår alle 7 trin på `patient.yml`,
forklarer crow's foot notation og viser, hvordan du tegner diagrammet i pgAdmins ERD Tool.

## 5. SQL: opret en tabel

```sql
CREATE TABLE patient (
    patient_id  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    first_name  TEXT    NOT NULL,
    age         INTEGER NOT NULL CHECK (age BETWEEN 0 AND 150)
    -- ...
);
```

- Kolonner adskilles med kommaer, og **der er intet komma efter den sidste kolonne**.
- `DROP TABLE IF EXISTS patient;` sletter tabellen, så du kan køre scriptet igen.
  **Det sletter også alle data i tabellen.**

## 6. CRUD = de fire grundlæggende operationer

| Bogstav | Operation | SQL |
|---|---|---|
| **C** | Create | `INSERT INTO patient (first_name, age) VALUES ('Anna', 45);` |
| **R** | Read | `SELECT * FROM patient WHERE patient_id = 1;` |
| **U** | Update | `UPDATE patient SET age = 46 WHERE patient_id = 1;` |
| **D** | Delete | `DELETE FROM patient WHERE patient_id = 1;` |

> ⚠️ `UPDATE` og `DELETE` **uden `WHERE`** ændrer eller sletter **alle rækker**. Skriv altid `WHERE` først.

`RETURNING patient_id` i slutningen af et `INSERT` giver dig det id, databasen valgte.

## 7. psycopg 3: tal med PostgreSQL fra Python

```python
import psycopg

with psycopg.connect("postgresql://postgres:postgres@localhost:5432/sundhedsapp") as conn:
    rows = conn.execute("SELECT * FROM patient").fetchall()
```

- **Connection** (`conn`) er en åben linje til databasen.
- **`conn.execute(query)`** kører ét statement og returnerer en **cursor**.
- **Cursor** holder resultatet. Brug `.fetchone()` for at få én række som en tuple (eller `None`),
  `.fetchall()` for at få en liste af tuples, og `.rowcount` for at se, hvor mange rækker der blev ændret.
- **Transaction**: ændringer gemmes ikke, før de er **committed**. `with`-blokken committer,
  når den slutter uden fejl, og laver **rollback** (fortryder alt), hvis der opstår en exception.

## 8. Byg aldrig SQL med f-strings (SQL injection)

```python
# ❌ FARLIGT
conn.execute(f"SELECT * FROM patient WHERE last_name = '{name}'")
```

En f-string bliver **straks lavet om til almindelig tekst**. Hvis `name` er `x' OR '1'='1`, bliver SQL'en
`... WHERE last_name = 'x' OR '1'='1'`, som returnerer **alle patienter**. Det er **SQL injection**.
Det er et af de mest almindelige sikkerhedshuller på nettet.

Løsningen er at **holde SQL og værdier adskilt**, så en værdi aldrig kan blive til SQL.
psycopg giver dig to måder at gøre det på: t-strings og `%s` placeholders.

## 9. t-strings: sikre queries i Python 3.14

Python 3.14 tilføjede **template strings** ([PEP 750](https://peps.python.org/pep-0750/)).
De ligner f-strings, men starter med `t`:

```python
name = "Holm"
f"WHERE last_name = {name}"   # -> 'WHERE last_name = Holm'   (en str: værdien er bagt ind)
t"WHERE last_name = {name}"   # -> Template(...)              (SQL og værdi forbliver adskilt)
```

En t-string er **ikke** en streng. Det er et `Template`-objekt, der husker tekstdelene og
værdierne hver for sig. psycopg 3.3+ læser det og sender værdierne til PostgreSQL **som parametre**,
præcis lige så sikkert som `%s`:

```python
# ✅ SIKKERT: psycopg laver {name} om til en parameter
conn.execute(t"SELECT * FROM patient WHERE last_name = {name}")
```

Hvorfor vi kan lide t-strings:

- Værdien står **lige der, hvor den bruges**, uden at tælle `%s` eller matche rækkefølgen i en tuple.
- Ingen fælde med tuple med ét element (se nedenfor).
- Du kan ikke komme til at sende en f-string ved en fejl, fordi psycopg kan se forskellen.

**Format specifiers** (valgfrie) skrives efter et kolon:

| Specifier | Betydning | Eksempel |
|---|---|---|
| *(ingen)* eller `:s` | en værdi, sendt som parameter (det normale) | `{age}` |
| `:i` | en **identifier**: et tabel- eller kolonnenavn | `ORDER BY {column:i}` |
| `:l` | en literal, der flettes ind i SQL'en på klienten | sjældent nødvendig |
| `:q` | et stykke SQL: en anden t-string | avanceret |

> ⚠️ Værdier kan aldrig bruges som tabel- eller kolonnenavne. `ORDER BY {column}` virker **ikke**.
> Brug `{column:i}`, og kun med kolonnenavne, du har tjekket mod en allow-list.

## 10. `%s` placeholders: den klassiske måde

Før Python 3.14 skrev man `%s`, hvor værdien skal stå, og sendte værdierne separat:

```python
conn.execute("SELECT * FROM patient WHERE last_name = %s", (name,))
```

- Brug altid `%s`, uanset typen (også til tal).
- Parametrene er en **tuple** i samme rækkefølge som `%s`. Én værdi kræver et komma til sidst:
  `(name,)`. `(name)` er bare `name` i parenteser.

Du vil se `%s` i de fleste tutorials og i ældre kode, og du **skal** bruge det til `executemany()`.

## 11. `executemany()`: mange rækker i ét kald

For at indsætte 1000 patienter *kunne* du kalde `execute()` 1000 gange. `executemany()` kører den samme
SQL én gang per element i en liste, og psycopg sender dem effektivt:

```python
rows = [("Kevin", "Holm", 34, "O+", None),
        ("Lone", "Kellerman", 66, "A+", "Peanuts")]

with get_connection() as conn, conn.cursor() as cursor:
    cursor.executemany(
        "INSERT INTO patient (first_name, last_name, age, blood_type, allergies) "
        "VALUES (%s, %s, %s, %s, %s)",
        rows,
    )
```

- **Hvorfor `%s` og ikke en t-string her?** En t-string fanger værdierne for *én* række i det øjeblik,
  den oprettes. `executemany()` skal bruge *én* query med tomme pladser (`%s`) og en *liste* af rækker
  at fylde dem med.
- `executemany()` findes på **cursoren**, ikke på connection, så vi åbner en med `conn.cursor()`.
- Hele listen er én transaction: hvis række 500 fejler, bliver række 1–499 også rullet tilbage.
- Det fungerer på samme måde for `UPDATE` og `DELETE`. Hvert element er en tuple, der matcher `%s` placeholders:

```python
cursor.executemany("UPDATE patient SET age = %s WHERE patient_id = %s", [(35, 1), (67, 2)])
cursor.executemany("DELETE FROM patient WHERE patient_id = %s", [(3,), (4,)])
```

| Brug | Hvornår |
|---|---|
| `conn.execute(t"...")` | ét statement med værdier (vores CRUD-funktioner) |
| `cursor.executemany("... %s ...", rows)` | det samme statement for mange rækker |

## 12. Hent API'et fra lektion 4 ind

Patienterne ligger allerede bag dit API fra lektion 4, beskyttet af et **bearer token**:

1. `POST /token/1` returnerer `{"token": "Bearer eyJ..."}`
2. `GET /health_data` med headeren `Authorization: Bearer eyJ...` returnerer patienterne.

I øvelsen henter du patienterne på denne måde, **renser** dem (`false` / `'No'` bliver til `NULL`) og
gemmer dem med `executemany()`. At flytte data fra en fil over i en database på denne måde kaldes en *migration*.

---

### Test dig selv

1. Hvad sker der, hvis du kører `DELETE FROM patient;`?
2. Hvad er forskellen på `f"... {x}"` og `t"... {x}"`, når du sender den til `conn.execute()`?
3. Hvorfor er `(5)` forkert som parameter til `WHERE patient_id = %s`?
4. Hvorfor kan du ikke bruge en t-string med `executemany()`?
5. Hvad gør `with`-blokken, hvis der opstår en exception halvvejs igennem?
6. Hvorfor gemme "ingen allergi" som `NULL` og ikke som teksten `'No'`?

---

## Læs mere

**PostgreSQL**
- [PostgreSQL tutorial (officiel)](https://www.postgresql.org/docs/current/tutorial.html). Kapitel 1–2 dækker tabeller og queries.
- [CREATE TABLE](https://www.postgresql.org/docs/current/sql-createtable.html)
- [Constraints](https://www.postgresql.org/docs/current/ddl-constraints.html). NOT NULL, CHECK, PRIMARY KEY.
- [Identity columns](https://www.postgresql.org/docs/current/ddl-identity-columns.html)
- [Data manipulation: INSERT, UPDATE, DELETE, RETURNING](https://www.postgresql.org/docs/current/dml.html)
- [W3Schools SQL tutorial](https://www.w3schools.com/sql/). Korte eksempler, du kan prøve i browseren.

**psycopg 3**
- [Basic module usage](https://www.psycopg.org/psycopg3/docs/basic/usage.html)
- [Template string queries (t-strings)](https://www.psycopg.org/psycopg3/docs/basic/tstrings.html)
- [Passing parameters to SQL queries (%s)](https://www.psycopg.org/psycopg3/docs/basic/params.html)
- [Transactions management](https://www.psycopg.org/psycopg3/docs/basic/transactions.html)
- [Cursor classes: execute() og executemany()](https://www.psycopg.org/psycopg3/docs/api/cursors.html)

**Python og sikkerhed**
- [PEP 750: Template strings](https://peps.python.org/pep-0750/)
- [What's new in Python 3.14](https://docs.python.org/3.14/whatsnew/3.14.html)
- [OWASP: SQL injection](https://owasp.org/www-community/attacks/SQL_Injection)

**ER diagrammer og pgAdmin**
- [er_design_guide.md](er_design_guide.md): vores 7-trins-metode
- [pgAdmin: ERD Tool](https://www.pgadmin.org/docs/pgadmin4/latest/erd_tool.html)
- [Lucidchart: What is an ER diagram?](https://www.lucidchart.com/pages/er-diagrams)
