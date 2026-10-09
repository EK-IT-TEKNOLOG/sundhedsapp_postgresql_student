# Del 2 – Teori: hospitaler, relationships, GROUP BY og stored procedures

Læs dette før undervisningen (ca. 35 minutter). Slides'ene `del2_theory.pptx` dækker de samme
emner og viser, hvordan du løser hvert trin i øvelsen.

---

## 1. Fra én tabel til tre

I del 1 havde vi én tabel: `patient`. Nu skal sundhedsappen også vide, **hvilken læge** en patient
har, og **hvilket hospital** lægen arbejder på. Den nemme (og forkerte) løsning er at tilføje
kolonnerne direkte i `patient`:

| patient_id | first_name | doctor_name | hospital_name | bed_count |
|---|---|---|---|---|
| 1 | Kevin | Mette Sørensen | Rigshospitalet | 1100 |
| 2 | Karen | Mette Sørensen | Rigshospitalet | 1100 |
| 3 | Erik | Mette Sørensen | Rigshospitalet | 1100 |

Se på gentagelserne. Hvis Rigshospitalet får flere senge, skal du ændre **alle** rækkerne, og glemmer
du én, er data uenige med sig selv. Det kaldes **redundans**, og det er præcis det, trin 7 i
ER-metoden fra del 1 advarede imod: *"Beskriver hver kolonne denne entity?"*

Løsningen er **én tabel per ting** og en **reference** mellem dem:

```
hospital  1 ──< mange  doctor  1 ──< mange  patient
```

Hver oplysning står nu ét sted. Rigshospitalets sengetal står i én række i `hospital`.

## 2. Relationships og foreign keys

En **foreign key (FK)** er en kolonne, der indeholder en **primary key fra en anden tabel**.

```sql
CREATE TABLE doctor (
    doctor_id    INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    hospital_id  INTEGER NOT NULL REFERENCES hospital (hospital_id),
    ...
);
```

`REFERENCES hospital (hospital_id)` betyder: *værdien i `doctor.hospital_id` skal findes i
`hospital.hospital_id`*. Databasen håndhæver reglen begge veje:

| Du prøver at … | Databasen svarer |
|---|---|
| indsætte en læge på hospital 99, som ikke findes | `ForeignKeyViolation: Key (hospital_id)=(99) is not present in table "hospital"` |
| slette et hospital, der stadig har læger | `ForeignKeyViolation: Key (hospital_id)=(1) is still referenced from table "doctor"` |

Det kaldes **referentiel integritet**: der kan aldrig opstå en læge, der peger på et hospital, som
ikke findes.

### Hvor skal foreign key'en stå?

Sig relationship'et højt i begge retninger, og find **"mange"-siden**:

- *Et hospital har **mange** læger. En læge arbejder på **ét** hospital.*
  → FK'en står i `doctor`: `doctor.hospital_id`
- *En læge har **mange** patienter. En patient har **én** (egen) læge.*
  → FK'en står i `patient`: `patient.doctor_id`

> 💡 **Reglen:** i et one-to-many relationship står foreign key'en altid på **mange**-siden.
> Et hospital kan ikke have en kolonne `doctor_id`, for der er ikke plads til mange læger i én celle.

### Crow's foot (fra del 1)

```
  HOSPITAL ──||────────o<── DOCTOR ──||────────o<── PATIENT
```

`||` = præcis én, `o<` = nul eller flere. Bornholms Hospital har (endnu) nul læger, og det er tilladt.

### Many-to-many (til diskussion)

I virkeligheden kan en patient se *flere* læger, og en læge har *flere* patienter. Det er
**many-to-many**, og det kan ikke laves med én FK. Man laver i stedet en **mellemtabel**, fx
`treatment(patient_id FK, doctor_id FK, date)`. Vi holder os til one-to-many i del 2 (ekstraopgave).

## 3. Den udleverede SQL, og hvad vi forbedrer

Opgaven giver os denne SQL som udgangspunkt:

```sql
CREATE TABLE Doctor (
    Doctor_Id INTEGER NOT NULL PRIMARY KEY,
    Doctor_Name TEXT NOT NULL,
    Hospital_Id INTEGER NOT NULL,
    Joining_Date TEXT NOT NULL,
    ...
);
```

Den virker, men har fire svagheder:

| Svaghed | Problem | Vores løsning |
|---|---|---|
| `Hospital_Id INTEGER` uden reference | intet stopper en læge på hospital 99 | `REFERENCES hospital (hospital_id)` |
| `Joining_Date TEXT` | `'2024-13-45'` og `'i går'` accepteres, og du kan ikke regne med datoer | `DATE` |
| `INTEGER NOT NULL PRIMARY KEY` | vi skal selv finde på alle id'er | `GENERATED ALWAYS AS IDENTITY` (som i del 1) |
| `Hospital_Id`, `Doctor_Name` | se nedenfor | `hospital_id`, `doctor_name` |

**Store og små bogstaver:** PostgreSQL laver alle navne uden anførselstegn om til små bogstaver.
`CREATE TABLE Hospital (Hospital_Id ...)` opretter altså tabellen `hospital` med kolonnen `hospital_id`.
Skriver du navnet i anførselstegn (`"Hospital_Id"`), gemmes de store bogstaver, og så skal du bruge
anførselstegn **hver gang** bagefter. Derfor: skriv altid `snake_case` med små bogstaver.

Vi tilføjer også to regler: `hospital_name` er `UNIQUE` (to hospitaler med samme navn giver ingen mening),
og `salary` og `bed_count` må ikke være negative (`CHECK`).

## 4. Rækkefølgen betyder noget

Når tabeller peger på hinanden, skal du tænke over rækkefølgen:

| Handling | Rækkefølge | Hvorfor |
|---|---|---|
| `CREATE TABLE` | hospital → doctor → patient | man kan kun referere til en tabel, der findes |
| `INSERT` | hospital → doctor → patient | en læge kan kun pege på et hospital, der findes |
| `DELETE` / `DROP` | patient → doctor → hospital | man kan ikke fjerne noget, andre peger på |

To genveje, vi bruger:

```sql
DROP TABLE IF EXISTS patient, doctor, hospital;            -- alle tre på én gang
TRUNCATE patient, doctor, hospital RESTART IDENTITY;       -- tøm alle tre, og start id'er ved 1
```

Når du nævner alle tabellerne i samme statement, klarer PostgreSQL rækkefølgen selv.

## 5. JOIN: læs fra flere tabeller på én gang

Data ligger nu i tre tabeller. For at se *"lægens navn og hospitalets navn"* skal vi sætte rækkerne
sammen igen. Det gør `JOIN`:

```sql
SELECT d.doctor_name, h.hospital_name
FROM doctor AS d
JOIN hospital AS h ON h.hospital_id = d.hospital_id;
```

- `AS d` og `AS h` er **aliaser**: korte navne, så vi kan skrive `d.doctor_name` i stedet for
  `doctor.doctor_name`. Når to tabeller har en kolonne med samme navn (`hospital_id`), **skal** du
  sige, hvilken tabel du mener.
- `ON` fortæller, **hvilke rækker der hører sammen**: foreign key = primary key.

> ⚠️ Glemmer du `ON` (fx `FROM doctor, hospital`), får du **alle kombinationer**: 9 læger × 5 hospitaler
> = 45 rækker. Det kaldes et *kartesisk produkt*, og det er næsten altid en fejl.

### INNER JOIN og LEFT JOIN

| Type | Giver | Eksempel |
|---|---|---|
| `JOIN` (= `INNER JOIN`) | kun rækker, der har et match i begge tabeller | hospitaler **med** læger |
| `LEFT JOIN` | **alle** rækker fra venstre tabel, og `NULL` hvor der ikke er et match | **alle** hospitaler, også Bornholm |

```sql
SELECT h.hospital_name, d.doctor_name
FROM hospital AS h
LEFT JOIN doctor AS d ON d.hospital_id = h.hospital_id;
-- ...
-- Bornholms Hospital | NULL
```

## 6. Aggregatfunktioner: regn på mange rækker

En **aggregatfunktion** tager mange rækker og giver **én værdi**:

| Funktion | Giver | Eksempel |
|---|---|---|
| `COUNT(*)` | antal rækker | `SELECT COUNT(*) FROM doctor;` → 9 |
| `COUNT(kolonne)` | antal rækker, hvor kolonnen **ikke er NULL** | `COUNT(experience)` → 7 |
| `SUM(kolonne)` | summen | `SUM(bed_count)` |
| `AVG(kolonne)` | gennemsnittet | `AVG(salary)` |
| `MIN(kolonne)` / `MAX(kolonne)` | mindste / største værdi | `MAX(salary)` |

> 💡 Aggregatfunktioner **springer NULL over**. To læger har `experience = NULL`, så
> `COUNT(*)` er 9, men `COUNT(experience)` er 7, og `AVG(experience)` er gennemsnittet af de 7.

`AVG` giver et decimaltal (`66333.3333…`). `AVG(salary)::integer` *caster* det til et heltal og runder.
`::` er PostgreSQLs måde at skrive "lav om til typen …".

## 7. GROUP BY: én række per gruppe

Uden `GROUP BY` giver `COUNT(*)` ét tal for hele tabellen. Med `GROUP BY` deles rækkerne op i
**grupper**, og aggregatfunktionen regnes **per gruppe**:

```sql
SELECT speciality, COUNT(*) AS doctors, AVG(salary)::integer AS avg_salary
FROM doctor
GROUP BY speciality;
```

```
 speciality     | doctors | avg_salary
----------------+---------+-----------
 Almen medicin  |       2 |      55000
 Kardiologi     |       3 |      66333
 Ortopædkirurgi |       2 |      71000
 Pædiatri       |       2 |      56500
```

Forestil dig det sådan: PostgreSQL lægger lægerne i bunker, én bunke per speciale, og tæller så
hver bunke.

**Den vigtigste regel:** hver kolonne i `SELECT` skal enten stå i `GROUP BY` **eller** være inde i en
aggregatfunktion. Ellers fejler det:

```sql
SELECT speciality, doctor_name, COUNT(*) FROM doctor GROUP BY speciality;
-- ERROR: column "doctor.doctor_name" must appear in the GROUP BY clause
--        or be used in an aggregate function
```

Hvorfor? Bunken "Kardiologi" har *tre* læger. Hvilket navn skulle PostgreSQL vise? Det kan den ikke vide.

### GROUP BY med JOIN

Du kan gruppere på tværs af tabeller. Her tæller vi læger per hospital, og `LEFT JOIN` sikrer, at
Bornholm kommer med:

```sql
SELECT h.hospital_name, COUNT(d.doctor_id) AS doctors
FROM hospital AS h
LEFT JOIN doctor AS d ON d.hospital_id = h.hospital_id
GROUP BY h.hospital_name;
```

> ⚠️ Brug `COUNT(d.doctor_id)`, ikke `COUNT(*)`. Bornholm har én række med `doctor_id = NULL`, så
> `COUNT(*)` giver 1, mens `COUNT(d.doctor_id)` giver det rigtige tal: 0.

## 8. HAVING: filtrér grupper

`WHERE` filtrerer **rækker**. `HAVING` filtrerer **grupper**, efter de er talt op:

```sql
SELECT speciality, COUNT(*) AS doctors
FROM doctor
GROUP BY speciality
HAVING COUNT(*) >= 3;          -- kun specialer med mindst 3 læger
```

Du kan ikke bruge `WHERE COUNT(*) >= 3`:

```
ERROR: aggregate functions are not allowed in WHERE
```

Grunden er den rækkefølge, PostgreSQL udfører en query i. Den er **ikke** den rækkefølge, du skriver den i:

| Skridt | Del | Hvad sker der |
|---|---|---|
| 1 | `FROM` / `JOIN` | find rækkerne, og sæt tabellerne sammen |
| 2 | `WHERE` | smid **rækker** væk (her findes der endnu ingen grupper) |
| 3 | `GROUP BY` | læg rækkerne i bunker |
| 4 | `HAVING` | smid **bunker** væk (nu kan vi tælle) |
| 5 | `SELECT` | vælg kolonner, og regn aggregater |
| 6 | `ORDER BY` | sortér resultatet |

Du kan bruge begge i samme query:

```sql
SELECT speciality, AVG(salary)::integer
FROM doctor
WHERE hospital_id = 1              -- kun rækker fra Rigshospitalet
GROUP BY speciality
HAVING AVG(salary) > 60000;        -- kun grupper med høj gennemsnitsløn
```

> 💡 **Tommelfingerregel:** kan betingelsen afgøres ud fra én række, så brug `WHERE`. Skal du tælle
> eller regne på en gruppe først, så brug `HAVING`.

Fra Python er det helt som i del 1: en værdi i `HAVING` er en t-string-parameter.

```python
conn.execute(t"SELECT speciality, COUNT(*) FROM doctor GROUP BY speciality "
             t"HAVING COUNT(*) >= {min_doctors}")
```

## 9. Stored procedures: kode, der bor i databasen

Indtil nu har al logik ligget i Python, og databasen har kun gemt data. Man kan også gemme **kode i
databasen** og kalde den ved navn. I PostgreSQL findes to slags:

| | `FUNCTION` | `PROCEDURE` |
|---|---|---|
| Formål | **returnerer** data | **udfører** en handling |
| Kaldes med | `SELECT * FROM navn(...)` | `CALL navn(...)` |
| Eksempel | `doctors_by_speciality('Kardiologi')` | `raise_salary('Pædiatri', 10)` |

I daglig tale kalder man begge for *stored procedures*.

### En function

```sql
CREATE OR REPLACE FUNCTION doctors_by_speciality(p_speciality TEXT)
RETURNS TABLE (doctor_name TEXT, hospital_name TEXT, salary INTEGER)
LANGUAGE sql
AS $$
    SELECT d.doctor_name, h.hospital_name, d.salary
    FROM doctor AS d
    JOIN hospital AS h ON h.hospital_id = d.hospital_id
    WHERE d.speciality = p_speciality
    ORDER BY d.salary DESC;
$$;
```

| Del | Betydning |
|---|---|
| `CREATE OR REPLACE` | opret, eller erstat en eksisterende. Du kan køre filen igen. |
| `(p_speciality TEXT)` | parameteren. `p_` gør det tydeligt, at det ikke er en kolonne. |
| `RETURNS TABLE (...)` | function'en returnerer rækker med disse kolonner |
| `LANGUAGE sql` | kroppen er almindelig SQL |
| `$$ ... $$` | kroppen. `$$` er anførselstegn, så du kan skrive `'` inde i koden. |

### En procedure med PL/pgSQL

Skal koden træffe beslutninger (`IF`) eller melde en fejl, bruger vi sproget **PL/pgSQL**:

```sql
CREATE OR REPLACE PROCEDURE raise_salary(p_speciality TEXT, p_percent INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE doctor
    SET salary = salary + salary * p_percent / 100
    WHERE speciality = p_speciality;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Ingen læger med specialet %', p_speciality;
    END IF;
END;
$$;
```

- `BEGIN ... END;` omslutter koden. Hvert statement slutter med `;`.
- `FOUND` er `true`, hvis det sidste statement ramte mindst én række.
- `RAISE EXCEPTION` stopper proceduren, **ruller UPDATE'en tilbage** og sender en fejl til klienten.
  `%` bliver erstattet af værdien efter kommaet.

### Kald fra Python

Præcis som alle andre queries, med t-strings:

```python
conn.execute(t"SELECT * FROM doctors_by_speciality({speciality})").fetchall()
conn.execute(t"CALL raise_salary({speciality}, {percent})")
```

En `RAISE EXCEPTION` bliver til en Python-exception af typen `psycopg.errors.RaiseException`:

```python
from psycopg.errors import RaiseException

try:
    raise_salary("Tandlæge", 10)
except RaiseException as error:
    logger.warning("Afvist: %s", error.diag.message_primary)
```

### Hvorfor (og hvorfor ikke)?

| Fordele | Ulemper |
|---|---|
| Logikken ligger ét sted og virker for **alle** programmer, der bruger databasen | Logikken er delt mellem Python og SQL, så den er sværere at overskue |
| Kun én tur frem og tilbage til databasen, selv for mange statements | Sværere at teste og versionsstyre end Python-kode |
| Reglerne kan ikke omgås af et program, der "glemmer" dem | PL/pgSQL er et ekstra sprog at lære |

> 💡 En god tommelfingerregel: regler om **data** (constraints, "løn må kun stige i procent") hører
> hjemme i databasen. Regler om **brugeren** (login, visning) hører hjemme i Python. Det er emnet for del 3.

---

### Test dig selv

1. Et hospital har mange læger. I hvilken tabel står foreign key'en, og hvorfor ikke i den anden?
2. Hvad sker der, hvis du prøver at slette et hospital, der har læger?
3. Hvorfor er `Joining_Date TEXT` en dårlig idé? Nævn noget, du kan med `DATE`, men ikke med `TEXT`.
4. Hvad er forskellen på `JOIN` og `LEFT JOIN`? Hvornår får du `NULL`?
5. Hvorfor fejler `SELECT speciality, doctor_name, COUNT(*) FROM doctor GROUP BY speciality`?
6. Hvornår bruger du `WHERE`, og hvornår `HAVING`?
7. Hvad er forskellen på en `FUNCTION` og en `PROCEDURE`, og hvordan kalder du hver af dem?
8. Hvad sker der med `UPDATE`'en i `raise_salary`, når proceduren kalder `RAISE EXCEPTION`?

---

## Læs mere

**Relationships og design**
- [PostgreSQL: Foreign keys](https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-FK)
- [PostgreSQL tutorial: Foreign keys](https://www.postgresql.org/docs/current/tutorial-fk.html)
- [PostgreSQL: Identifiers og store/små bogstaver](https://www.postgresql.org/docs/current/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS)
- [PostgreSQL: Date/time types](https://www.postgresql.org/docs/current/datatype-datetime.html)
- [pgAdmin: ERD Tool](https://www.pgadmin.org/docs/pgadmin4/latest/erd_tool.html). Se *One-to-Many*.
- [Lucidchart: What is an ER diagram?](https://www.lucidchart.com/pages/er-diagrams)

**JOIN, GROUP BY og HAVING**
- [PostgreSQL tutorial: Joins between tables](https://www.postgresql.org/docs/current/tutorial-join.html)
- [PostgreSQL tutorial: Aggregate functions](https://www.postgresql.org/docs/current/tutorial-agg.html). Forklarer WHERE vs HAVING.
- [PostgreSQL: GROUP BY og HAVING](https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-GROUP)
- [PostgreSQL: Aggregate functions (liste)](https://www.postgresql.org/docs/current/functions-aggregate.html)
- [W3Schools: SQL JOIN](https://www.w3schools.com/sql/sql_join.asp), [GROUP BY](https://www.w3schools.com/sql/sql_groupby.asp), [HAVING](https://www.w3schools.com/sql/sql_having.asp)

**Stored procedures**
- [PostgreSQL: CREATE FUNCTION](https://www.postgresql.org/docs/current/sql-createfunction.html)
- [PostgreSQL: CREATE PROCEDURE](https://www.postgresql.org/docs/current/sql-createprocedure.html)
- [PostgreSQL: SQL functions](https://www.postgresql.org/docs/current/xfunc-sql.html)
- [PL/pgSQL: control structures (IF, FOUND)](https://www.postgresql.org/docs/current/plpgsql-control-structures.html)
- [PL/pgSQL: errors and messages (RAISE)](https://www.postgresql.org/docs/current/plpgsql-errors-and-messages.html)
- [psycopg: Errors (RaiseException, ForeignKeyViolation)](https://www.psycopg.org/psycopg3/docs/api/errors.html)
