# Del 3 – Øvelse: login med Flask og role-based access control

**Mål:** giv sundhedsappen et rigtigt login. Brugere og roller ligger i PostgreSQL, passwords er
hashede, API'et udleverer bearer tokens, og hver rolle må kun det, den skal.

**Når du er færdig, kan du:**

- udvide ER diagrammet med brugere og roller, inkl. et one-to-one relationship
- gemme passwords sikkert som hashes med salt
- bygge et `/login` endpoint, der udleverer et JWT bearer token med udløbstid
- beskytte endpoints med `@app.auth_required(auth, roles=[...])`
- forklare forskellen på `401` og `403` og teste adgangsreglerne automatisk

**Sådan arbejder du:**

- Arbejd i mappen `del3_login`. Deltrinene (2.2, 2.3 …) matcher `TODO`-numrene i koden.
- Efter hvert ✅ **Tjek** ved du, at den del virker. Gå ikke videre, før den gør.
- Sidder du fast? 1) Læs fejlbeskeden nedefra og op. 2) Læs hintet i `TODO`.
  3) Se på slidet for det trin. 4) Kig først derefter i `solution/`.

**Forudsætninger:** PostgreSQL, pgAdmin, databasen `sundhedsapp` og `uv sync` fra del 1. Kør
`uv sync` igen: del 3 bruger to nye pakker, `apiflask` og `joserfc`. Del 3 kræver ikke, at del 1
og 2 er færdige: `schema.sql` og `data.sql` opretter og fylder alle tabeller.

---

## Forberedelse (før undervisningen, ca. 35 min)

1. Kør `uv sync` i mappen `sundhedsapp_postgres`.
2. Læs [theory.md](theory.md), og besvar de otte spørgsmål under "Test dig selv".
3. Åbn `db.py` i denne mappe. Hvis dit password ikke er `postgres`, så ret det i `DATABASE_URL`.

---

> 🏠 **Trin 1–3 er en del af forberedelsen.** Lav dem hjemme, så tiden i undervisningen går til
> login, tokens og roller (trin 4–7).

## Trin 1: Udvid ER diagrammet med login (8 min)

1. **1.1 Indsaml:** hvad skal vi vide om en bruger for at kunne logge den ind og give den adgang?
   Skriv felterne ned. 💡 Hvilket felt må **aldrig** gemmes, som det er?
2. **1.2 Entities:** vi har brug for to nye: `app_user` og `role`. Hvorfor ikke bare `user`?
   (Prøv `SELECT user;` i Query Tool.)
3. **1.3 Relationships:** skriv to sætninger i hver retning, som i del 2:
   - bruger og rolle
   - bruger og læge (ikke alle brugere er læger, og en læge har højst én bruger)
4. **1.4 Cardinality:** hvilket relationship er one-to-many, og hvilket er one-to-one?
   Hvilken constraint gør en foreign key til one-to-one?
5. **1.5 Tegn:** åbn dit ERD fra del 2 (`hospital.pgerd`) i pgAdmin, eller lav et nyt med
   **ERD For Database**. Tilføj `role` og `app_user`, og forbind dem med **One-to-Many**
   (`app_user.role_id → role.role_id`, `app_user.doctor_id → doctor.doctor_id`).
6. **1.6 Gem:** gem diagrammet som `login.pgerd` i denne mappe.

✅ **Tjek:** 5 tabeller og 4 relationship-linjer. Sammenlign med [solution/er_diagram.md](solution/er_diagram.md).

## Trin 2: Opret tabellerne (6 min)

1. **2.1** Åbn [schema.sql](schema.sql). `hospital`, `doctor` og `patient` er færdige fra del 2.
2. **2.2** Opret tabellen `role`.
3. **2.3** Indsæt de tre roller `admin`, `doctor` og `nurse`.
4. **2.4** Gør `app_user` færdig med `password_hash`, `role_id` og `doctor_id`.
5. **2.5** Kør `schema.sql` i Query Tool (**F5**), og kør derefter [data.sql](data.sql).
   ⚠️ Det sletter tabellerne fra del 1 og 2 og laver dem forfra.
6. **2.6** Test dine constraints. Det **første skal virke, de næste to skal fejle**:

   ```sql
   INSERT INTO app_user (username, password_hash, role_id) VALUES ('test', 'x', 1);
   INSERT INTO app_user (username, password_hash, role_id) VALUES ('test', 'x', 1);
   INSERT INTO app_user (username, password_hash, role_id, doctor_id) VALUES ('test2', 'x', 1, 99);
   ```

✅ **Tjek:** `SELECT * FROM role;` viser 3 roller. Det andet `INSERT` fejler med
`duplicate key value violates unique constraint "app_user_username_key"`, og det tredje med
`violates foreign key constraint "app_user_doctor_id_fkey"`. (`test`-brugeren bliver slettet i trin 3.)

## Trin 3: Hash passwords, og opret brugere (7 min)

1. **3.1 Prøv hashing i Python-shellen.** Kør `uv run python`, og skriv:
   ```python
   >>> from werkzeug.security import generate_password_hash, check_password_hash
   >>> h1 = generate_password_hash("mette-pass")
   >>> h2 = generate_password_hash("mette-pass")
   >>> h1
   >>> h1 == h2
   >>> check_password_hash(h1, "mette-pass")
   >>> check_password_hash(h2, "mette-pass")
   >>> check_password_hash(h1, "Mette-pass")
   ```
   💡 `h1` og `h2` er forskellige, men begge passer til passwordet. Find **salt**-delen mellem de to `$`.
   (Teoriafsnit 3.) Skriv `exit()`, når du er færdig.
2. **3.2** Åbn [users.py](users.py). Læs `TEST_USERS` og SQL'en i `create_users()`. Hvordan finder
   subqueryen `role_id`? Lav `rows` med en list comprehension, der hasher hvert password.
3. **3.3** Kør `uv run users.py`.
4. **3.4** I pgAdmin: `SELECT username, password_hash, role_id, doctor_id FROM app_user;`

✅ **Tjek:** `Oprettede 4 brugere` og en dict for mette med et `password_hash`, der starter med
`scrypt:`. Derefter `NotImplementedError: trin 5.1`, og det er fint. Ingen passwords står i klartekst i pgAdmin.

💡 Hvad sker der, hvis du ændrer en rolle i `TEST_USERS` til `"admn"`? Prøv, læs fejlen, og ret tilbage.

---

## Trin 4: Login (9 min)

1. **4.1** Start app'en i en **ny terminal** i mappen `del3_login`, og lad den køre:
   ```bash
   uv run flask --app app run --port 5001 --debug
   ```
   `--debug` genstarter serveren, hver gang du gemmer. Port 5001, så den ikke støder sammen med
   lektion 4-appen på 5000.
2. **4.2** Åbn [auth.py](auth.py). Skriv `check_login()`.
3. **4.3** Åbn [app.py](app.py). Skriv `login()`: `abort(401, ...)` ved forkert login, ellers et token.
4. **4.4** Åbn <http://127.0.0.1:5001/docs>, og prøv **POST /login** (*Try it out*) med
   `{"username": "mette", "password": "mette-pass"}`. Prøv derefter med et forkert password og
   med et brugernavn, der ikke findes.

✅ **Tjek:** rigtigt login giver `200` og `{"token": "eyJ..."}`. Forkert password **og** ukendt
bruger giver begge `401` med **samme** besked: `Forkert brugernavn eller password`. Hvorfor samme besked?

## Trin 5: Tjek tokenet (7 min)

1. **5.1** Skriv `get_user()` i `users.py`. Den må **ikke** returnere `password_hash`.
2. **5.2** Skriv `verify_token()` i `auth.py` med `read_token()` og `get_user()`.
3. **5.3** I `/docs`: log ind som mette, og kopiér tokenet (uden anførselstegn). Klik **Authorize**,
   indsæt tokenet, og klik **Authorize**. Prøv **GET /me**. Klik derefter **Logout** i Authorize, og prøv igen.
4. **5.4 Læs dit token.** Et JWT er ikke krypteret. Kør `uv run python`:
   ```python
   >>> import base64, json
   >>> token = "indsæt dit token her"
   >>> header, payload, signature = token.split(".")
   >>> json.loads(base64.urlsafe_b64decode(payload + "=="))
   ```
   Du ser `{'sub': '2', 'exp': ...}`. Hvad ville der ske, hvis du ændrede `sub` til `'1'`?
   (Teoriafsnit 5.)
5. **5.5** Ret et enkelt tegn midt i tokenet i **Authorize**, og prøv **GET /me** igen.

✅ **Tjek:** med token: `200` og `{"username": "mette", "role": "doctor"}`. Uden token og med det
ændrede token: `401` og `"message": "Unauthorized"`.

## Trin 6: Roller (8 min)

1. **6.1** Skriv `get_user_roles()` i `auth.py`.
2. **6.2 Prøv først uden roller.** Log ind som `nina` (nurse) i `/docs`, og prøv **GET /my_patients**.
   Du får en fejl (`NotImplementedError: trin 6.3` i terminalen). Selv hvis funktionen virkede:
   hvad ville en sygeplejerske uden `doctor_id` få? Det er et tegn på, at endpointet mangler en regel.
3. **6.3** Skriv `patients_of_doctor()` i [patients.py](patients.py) med en t-string.
4. **6.4** Tilføj `roles=[...]` i `app.py` på `/patients`, `/my_patients` og `DELETE /patients/<id>`
   efter tabellen i teoriafsnit 6.
5. **6.5** Test i `/docs`:
   - som `nina`: **GET /patients** → `200`, **GET /my_patients** → `403`
   - som `mette`: **GET /my_patients** → kun hendes egne patienter, **GET /patients** → `403`
   - som `mette`: **DELETE /patients/{patient_id}** med id `999` → `403`

✅ **Tjek:** mette ser Kevin, Karen og Erik under `/my_patients`. `403`-svarene har
`"message": "Forbidden"`.

💡 Diskutér med din sidemand: hvorfor tager `/my_patients` ikke et læge-id i URL'en, fx `/my_patients/1`?

## Trin 7: Test alle regler på én gang (6 min)

At klikke rundt i `/docs` er langsomt og nemt at glemme. Vi lader et script gøre det.

1. **7.1** Lad app'en køre. Åbn [client.py](client.py) i en **anden terminal**.
2. **7.2** Skriv `login()`: `POST /login` med `json=`, `raise_for_status()`, returnér tokenet.
3. **7.3** Lav `headers` i `status_code()`: med token `{"Authorization": f"Bearer {token}"}`, ellers `{}`.
4. **7.4** Kør `uv run client.py`.

✅ **Tjek:** outputtet skal være præcis denne tabel:

```
                              admin       mette        nina  uden token
GET /me                         200         200         200         401
GET /patients                   200         403         200         401
GET /my_patients                403         200         403         401
DELETE /patients/999            404         403         403         401
Forkert password giver: 401
```

Sammenlign med tabellen i teoriafsnit 6. Hvorfor giver admin `404` og ikke `204` på `DELETE`?

💡 Denne tabel er en **test**. Ændrer nogen en `roles=[...]` ved en fejl, ændrer tabellen sig. I del 4
gør vi den slags tjek automatisk med pytest.

---

## Ekstra (hvis du har tid, eller hjemme)

1. **Udløb:** sæt `TOKEN_LIFETIME_SECONDS = 10` i `auth.py`. Log ind, vent 15 sekunder, og kald `/me`.
   Hvilken status code? Hvor i koden bliver det afgjort? Sæt værdien tilbage.
2. **Opret patienter:** lav `POST /patients` for `admin` og `nurse` med en `PatientIn`-schema (som
   `/add_patient` i lektion 4) og en `create_patient()`-funktion med `RETURNING patient_id`.
   Hvad svarer databasen, når blodtypen er `"X+"`, og hvordan vil du vise det til klienten?
3. **Skift password:** lav `POST /me/password`, der tager det gamle og det nye password. Tjek det gamle
   med `check_password_hash`, og gem det nye som et hash.
4. **Flere roller per bruger:** en overlæge er både `doctor` og `admin`. Tegn en mellemtabel
   `user_role(user_id, role_id)` (many-to-many fra del 2). `get_user_roles()` må gerne returnere en
   liste. Hvad skal ændres i `get_user()`?
5. **Roller i selve databasen:** PostgreSQL har også roller. Lav en database-bruger til app'en, der
   kun må læse og skrive `patient`:
   `CREATE ROLE sundhedsapp_api LOGIN PASSWORD '...'; GRANT SELECT, INSERT, DELETE ON patient TO sundhedsapp_api;`
   Hvad sker der, når den prøver `SELECT * FROM app_user`? Hvorfor er det least privilege?

## Refleksion

Skriv 2–3 sætninger i dine egne noter:

- Hvad var de to største sikkerhedsproblemer i lektion 4's token-endpoint, og hvordan løste du dem?
- Forklar forskellen på `401` og `403` med et eksempel fra sundhedsappen.
- Hvilke data ville du aldrig lægge i et JWT, og hvorfor?

## Læs mere

Se linklisten nederst i [theory.md](theory.md#læs-mere).
