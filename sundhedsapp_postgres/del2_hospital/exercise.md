# Del 2 – Øvelse: hospitaler, læger og patienter

**Mål:** udvid sundhedsappen fra én tabel til tre (`hospital`, `doctor`, `patient`), forbind dem med
foreign keys, og stil spørgsmål til data med `JOIN`, `GROUP BY`, `HAVING` og stored procedures.

**Når du er færdig, kan du:**

- udvide et ER diagram med one-to-many relationships og placere foreign key'en rigtigt
- forbedre en udleveret `CREATE TABLE` med `REFERENCES`, `DATE` og `IDENTITY`
- indsætte data i flere tabeller i den rigtige rækkefølge med `executemany()`
- sætte tabeller sammen med `JOIN` og `LEFT JOIN`
- tælle og regne per gruppe med `GROUP BY` og filtrere grupper med `HAVING`
- skrive en `FUNCTION` og en `PROCEDURE` i PostgreSQL og kalde dem fra Python

**Sådan arbejder du:**

- Arbejd i mappen `del2_hospital`. Deltrinene (2.2, 2.3 …) matcher `TODO`-numrene i koden.
- Efter hvert ✅ **Tjek** ved du, at den del virker. Gå ikke videre, før den gør.
- **Skriv SQL i pgAdmin først.** Query Tool viser resultatet med det samme. Når det er rigtigt,
  kopierer du det over i Python.
- Sidder du fast? 1) Læs fejlbeskeden nedefra og op. 2) Læs hintet i `TODO`.
  3) Se på slidet for det trin. 4) Kig først derefter i `solution/`.

**Forudsætninger:** PostgreSQL, pgAdmin, databasen `sundhedsapp` og `uv sync` fra del 1 (P1–P3).
Del 2 kan laves, selvom du ikke blev færdig med del 1: `schema.sql` opretter alle tabeller forfra.

---

## Forberedelse (før undervisningen, ca. 35 min)

1. Læs [theory.md](theory.md), og besvar de otte spørgsmål under "Test dig selv".
2. Kig på trin 7 i [../del1_database_crud/er_design_guide.md](../del1_database_crud/er_design_guide.md)
   igen: *"Beskriver hver kolonne denne entity?"* Det er udgangspunktet for i dag.
3. Åbn `db.py` i denne mappe. Hvis dit password ikke er `postgres`, så ret det i `DATABASE_URL`.

---

> 🏠 **Trin 1–3 er en del af forberedelsen.** Lav dem hjemme, så tiden i undervisningen går til
> JOIN, GROUP BY, HAVING og stored procedures (trin 4–7).

## Trin 1: Udvid ER diagrammet (10 min)

Skriv dine svar på papir eller i en tekstfil først, og **tegn** først bagefter.

1. **1.1 Udgangspunkt:** du har én entity fra del 1: `patient`. Opgaven giver dig SQL til to nye:

   ```sql
   CREATE TABLE Hospital (
       Hospital_Id INTEGER NOT NULL PRIMARY KEY,
       Hospital_Name TEXT NOT NULL,
       Bed_Count INTEGER NOT NULL
   );

   CREATE TABLE Doctor (
       Doctor_Id INTEGER NOT NULL PRIMARY KEY,
       Doctor_Name TEXT NOT NULL,
       Hospital_Id INTEGER NOT NULL,
       Joining_Date TEXT NOT NULL,
       Speciality TEXT NOT NULL,
       Salary INTEGER NOT NULL,
       Experience INTEGER
   );
   ```

2. **1.2 Entities:** skriv de tre entities ned med navne i ental og små bogstaver.
3. **1.3 Relationships:** skriv hvert relationship som **to sætninger**, én i hver retning.
   Eksempel: *"Et hospital har mange læger. En læge arbejder på ét hospital."*
   Gør det samme for læge og patient.
4. **1.4 Foreign keys:** hvilken tabel er "mange"-siden i hvert relationship? Dér skal foreign key'en
   stå. Hvilken kolonne mangler i `patient`?
5. **1.5 Kritik:** find **fire** svagheder i den udleverede SQL.
   💡 Hint: hvad stopper en læge på hospital 99? Hvad sker der med datoen `'i går'`? Hvem finder på
   id'erne? Hvad gør PostgreSQL ved `Hospital_Id`? (Teoriafsnit 3.)
6. **1.6 Tegn:** i pgAdmin, højreklik på `sundhedsapp`, og vælg **ERD For Database**.
   - Findes `patient` fra del 1, er den allerede på lærredet. Ellers tilføj den (se del 1, trin 1.7).
   - Klik **Add table** for `hospital` og `doctor`. Brug dine forbedrede navne og typer
     (`joining_date` = `date`), og sæt id'erne til **IDENTITY / ALWAYS**.
   - Tilføj kolonnen `doctor_id` (integer, Not NULL) i `patient`.
   - Marker `doctor` (mange-siden), og klik på **One-to-Many** i værktøjslinjen. Vælg
     Local column = `hospital_id`, Referenced table = `hospital`, Referenced column = `hospital_id`.
   - Gør det samme for `patient.doctor_id` → `doctor.doctor_id`.
7. **1.7 Gem:** gem diagrammet som `hospital.pgerd` i denne mappe.

✅ **Tjek:** 3 tabeller, 2 relationship-linjer med crow's foot ved `doctor` og `patient`, og
foreign keys i `doctor.hospital_id` og `patient.doctor_id`. Sammenlign med
[solution/er_diagram.md](solution/er_diagram.md).

## Trin 2: Opret tabellerne i SQL (6 min)

1. **2.1** Åbn [schema.sql](schema.sql). Læs den udleverede SQL øverst og de fire rettelser.
   `hospital` er færdig. Sammenlign den med den udleverede `Hospital`.
2. **2.2** Tilføj `hospital_id` i `doctor` med `REFERENCES hospital (hospital_id)`.
3. **2.3** Tilføj `joining_date` med typen `DATE`.
4. **2.4** Tilføj `doctor_id` i `patient` med `REFERENCES doctor (doctor_id)`.
   Husk kommaet efter `allergies TEXT`.
5. **2.5** Kør hele filen i Query Tool (**F5**). Refresh **Tables**: du skal se tre tabeller.
   ⚠️ Det sletter `patient` fra del 1. Det er meningen.
6. **2.6** Test din foreign key. Det **første skal virke, det andet skal fejle**:

   ```sql
   INSERT INTO hospital (hospital_name, bed_count) VALUES ('Testhospital', 10);

   INSERT INTO doctor (doctor_name, hospital_id, joining_date, speciality, salary)
   VALUES ('Dr. Ingen', 99, '2024-01-01', 'Test', 50000);
   ```

7. **2.7** Test din `DATE`. Dette skal fejle:

   ```sql
   INSERT INTO doctor (doctor_name, hospital_id, joining_date, speciality, salary)
   VALUES ('Dr. Dato', 1, 'i går', 'Test', 50000);
   ```

✅ **Tjek:** 2.6 fejler med `violates foreign key constraint "doctor_hospital_id_fkey"` og
`Key (hospital_id)=(99) is not present in table "hospital"`. 2.7 fejler med
`invalid input syntax for type date`. Hvis et af dem **ikke** fejlede, så ret `schema.sql`, og kør den igen.

## Trin 3: Fyld tabellerne (7 min)

1. **3.1** Start appen fra lektion 4 i en **anden terminal** (som i del 1, trin 7.1):
   ```bash
   cd "sundhedsapp/del4 visualisering"
   flask run
   ```
   Kører den ikke, bruger `seed.py` en kopi af `patient.yml`, og du får en advarsel. Det er i orden.
2. **3.2** Åbn [seed.py](seed.py). Læs listerne `HOSPITALS`, `DOCTORS` og `EXTRA_PATIENTS`, og
   funktionen `insert_hospitals()`. Skriv `insert_doctors()` på samme måde: seks kolonner, seks `%s`.
   Kør `uv run seed.py`. ✅ Du ser `Hospitaler: 5`, `Læger: 9` og derefter `NotImplementedError: trin 3.3`.
   💡 Se i pgAdmin: `SELECT * FROM hospital;`. Den er **tom**! Hvorfor? (Hint: hele `seed()` er
   **én transaction**. Teoriafsnit 7 i del 1.)
3. **3.3** Skriv `insert_patients()`. Bemærk: rækkerne kommer fra parameteren `rows`.
4. **3.4** Kør `uv run seed.py` igen.
5. **3.5** Prøv at slette et hospital i pgAdmin:
   ```sql
   DELETE FROM hospital WHERE hospital_id = 1;
   ```

✅ **Tjek:** `Hospitaler: 5`, `Læger: 9`, `Patienter: 12` (flere, hvis du tilføjede patienter i lektion 4).
3.5 fejler med `Key (hospital_id)=(1) is still referenced from table "doctor"`. Databasen passer på dine data.

💡 Hvorfor skal `HOSPITALS` indsættes før `DOCTORS`? Hvad ville der ske i omvendt rækkefølge?

---

## Trin 4: JOIN (7 min)

1. **4.1** Åbn [queries.py](queries.py), og læs `doctors_with_hospital()`. Kopiér SQL'en ind i
   Query Tool, og kør den. Fjern derefter `JOIN ... ON ...`-linjen, og skriv `FROM doctor AS d, hospital AS h`.
   Hvor mange rækker får du nu? Hvorfor? (Teoriafsnit 5.) Sæt `JOIN`'en tilbage.
2. **4.2** Skriv `patients_at_hospital(hospital_id)`. Test først i pgAdmin med `WHERE d.hospital_id = 1`.
   Kopiér den derefter ind som en t-string med `{hospital_id}`.
   💡 Du behøver ikke `hospital`-tabellen: `hospital_id` står allerede i `doctor`.
3. **4.3** Kør `uv run queries.py`.

✅ **Tjek:** 9 læger med hospitalsnavne, derefter 6 patienter på Rigshospitalet (Berg, Holm, Juhl,
Kellerman, Larsson, Lund), og derefter `NotImplementedError: trin 5.3`.

## Trin 5: GROUP BY (9 min)

Arbejd i pgAdmin i 5.1–5.4.

1. **5.1** Tæl læger per hospital-id:
   ```sql
   SELECT hospital_id, COUNT(*) FROM doctor GROUP BY hospital_id;
   ```
   Hvor mange rækker? Hvilket hospital mangler?
2. **5.2** Vis hospitalets navn i stedet: `JOIN` til `hospital`, og `GROUP BY h.hospital_name`.
   Bornholms Hospital er stadig ikke med. Hvorfor ikke?
3. **5.3** Skift til `LEFT JOIN` med `hospital` til venstre, og tæl med `COUNT(d.doctor_id)`.
   Skriv den færdige query i `doctors_per_hospital()`.
   🔬 Prøv `COUNT(*)` i stedet. Hvad viser Bornholm nu? Hvorfor? (Teoriafsnit 7.)
4. **5.4** Bryd reglen med vilje: tilføj `d.doctor_name` til `SELECT` i din query fra 5.3. Læs fejlen.
   Forklar din sidemand, **hvorfor** PostgreSQL ikke kan svare.
5. **5.5** Skriv `salary_by_speciality()` med `COUNT(*)`, `AVG(salary)::integer` og `MAX(salary)`.
6. **5.6** Kør `uv run queries.py`.

✅ **Tjek:**

```
Trin 5.3 Læger per hospital:
  ('Aarhus Universitetshospital', 3)
  ('Rigshospitalet', 3)
  ('Odense Universitetshospital', 2)
  ('Aalborg Universitetshospital', 1)
  ('Bornholms Hospital', 0)
Trin 5.5 Løn per speciale:
  ('Almen medicin', 2, 55000, 60000)
  ('Kardiologi', 3, 66333, 72000)
  ('Ortopædkirurgi', 2, 71000, 78000)
  ('Pædiatri', 2, 56500, 61000)
```

Derefter `NotImplementedError: trin 6.1`.

## Trin 6: HAVING (6 min)

1. **6.1** Skriv `specialities_with_min_doctors(min_doctors)` med `HAVING COUNT(*) >= {min_doctors}`
   som en t-string.
2. **6.2** I pgAdmin: prøv at skrive det samme med `WHERE COUNT(*) >= 3` i stedet for `HAVING`.
   Læs fejlen. Find svaret i tabellen over rækkefølgen i teoriafsnit 8.
3. **6.3** Kombinér: find specialer med en gennemsnitsløn over 60000, **kun blandt læger på
   Rigshospitalet** (`hospital_id = 1`). Hvilken betingelse skal i `WHERE`, og hvilken i `HAVING`?
4. **6.4** Skriv `well_paid_specialities(min_avg_salary)` med `HAVING AVG(salary) > {min_avg_salary}`.
5. **6.5** Kør `uv run queries.py`.

✅ **Tjek:** `('Kardiologi', 3)` under 6.1, og `('Ortopædkirurgi', 71000)` og `('Kardiologi', 66333)`
under 6.4. Ingen `NotImplementedError`. I 6.3 får du Kardiologi og Pædiatri.

## Trin 7: Stored procedures (8 min)

1. **7.1** Åbn [procedures.sql](procedures.sql), og læs function'en `doctors_by_speciality`. Find de
   fem dele fra teoriafsnit 9: navn og parameter, `RETURNS TABLE`, `LANGUAGE`, `$$` og kroppen.
2. **7.2** Kør hele filen i Query Tool (**F5**), og test function'en:
   ```sql
   SELECT * FROM doctors_by_speciality('Kardiologi');
   ```
   Refresh **Schemas → public → Functions** og **Procedures** i Object Explorer. Der er de.
3. **7.3** Skriv `UPDATE`'en i proceduren `raise_salary`. Kør filen igen (`CREATE OR REPLACE`), og test:
   ```sql
   CALL raise_salary('Pædiatri', 10);
   SELECT * FROM doctors_by_speciality('Pædiatri');
   CALL raise_salary('Tandlæge', 10);
   ```
   Den sidste skal fejle med **din egen** besked: `Ingen læger med specialet Tandlæge`.
4. **7.4** Åbn [procedures.py](procedures.py). Skriv `doctors_by_speciality()` med
   `t"SELECT * FROM doctors_by_speciality({speciality})"`.
5. **7.5** Skriv `raise_salary()` med `t"CALL raise_salary({speciality}, {percent})"`.
6. **7.6** I `main()`: kald `raise_salary("Tandlæge", 10)` inde i `try` / `except RaiseException as error:`,
   og log `error.diag.message_primary`.
7. **7.7** Kør `uv run seed.py` (nulstil lønningerne), og derefter `uv run procedures.py`.

✅ **Tjek:**

```
Pædiatri før:
  ('Sara Nielsen', 'Rigshospitalet', 61000)
  ('Emma Kristensen', 'Aarhus Universitetshospital', 52000)
Pædiatri efter 10 % lønstigning:
  ('Sara Nielsen', 'Rigshospitalet', 67100)
  ('Emma Kristensen', 'Aarhus Universitetshospital', 57200)
Afvist af proceduren: Ingen læger med specialet Tandlæge
```

💡 Diskutér med din sidemand: lønstigningen kunne også være skrevet i Python med en `UPDATE`.
Hvad vinder man ved at lægge den i databasen? Hvad taber man?

---

## Ekstra (hvis du har tid, eller hjemme)

1. **Tre tabeller på én gang:** skriv `hospitals_with_min_patients(min_patients)`, der tæller patienter
   per hospital (`hospital` → `doctor` → `patient`) og kun viser hospitaler med mindst `min_patients`.
   Med 2 skal du få Rigshospitalet (6) og Aarhus (4).
2. **Hvorfor DATE?** Tæl læger per ansættelsesår med `EXTRACT(YEAR FROM joining_date)` og `GROUP BY`.
   Kunne du gøre det, hvis `joining_date` var `TEXT`?
3. **Endnu en procedure:** skriv `move_doctor(p_doctor_id, p_hospital_id)`, der flytter en læge til et
   andet hospital. Brug `IF NOT EXISTS (SELECT 1 FROM hospital WHERE ...)` til at give en pæn fejl, hvis
   hospitalet ikke findes. Kald den fra Python.
4. **Many-to-many:** en patient kan se flere læger. Tegn en `treatment`-tabel i dit ERD med to foreign
   keys (`patient_id`, `doctor_id`) og en `treatment_date`. Hvad bliver primary key?
5. **ON DELETE:** læs om `ON DELETE CASCADE` og `ON DELETE SET NULL` i
   [dokumentationen](https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-FK).
   Hvad ville være bedst for `patient.doctor_id`, når en læge stopper? Hvorfor er `CASCADE` farligt her?

## Refleksion

Skriv 2–3 sætninger i dine egne noter:

- Hvorfor er tre tabeller bedre end én stor tabel med `hospital_name` i hver patientrække?
- Forklar forskellen på `WHERE` og `HAVING` med dine egne ord og et eksempel fra sundhedsappen.
- Hvilken regel ville du lægge i en stored procedure, og hvilken ville du beholde i Python?

## Læs mere

Se linklisten nederst i [theory.md](theory.md#læs-mere).
