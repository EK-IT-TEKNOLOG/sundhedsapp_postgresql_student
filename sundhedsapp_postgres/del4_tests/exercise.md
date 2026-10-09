# Del 4 – Øvelse: tests med pytest

**Mål:** skriv automatiske tests til sundhedsappen: først af små rene funktioner, derefter af
databasefunktionerne mod en frisk testdatabase, og til sidst af login og alle adgangsregler fra del 3.

**Når du er færdig, kan du:**

- skrive og køre tests med pytest og læse outputtet, når en test fejler
- bruge `parametrize` til mange eksempler og `pytest.raises` til forventede fejl
- bruge fixtures, inkl. `monkeypatch` og dine egne i `conftest.py`
- teste mod en rigtig PostgreSQL-database med pytest-postgresql, uden at røre dine egne data
- skrive en login-fixture og teste alle adgangsregler med én parametriseret test

**Sådan arbejder du:**

- Arbejd i mappen `del4_tests`. Du skriver kun i mappen `tests/`. App'en (`app.py`, `auth.py` …)
  er færdig fra del 3.
- Hver test med et `TODO` fejler med `NotImplementedError: trin X.Y`. Dit mål er at gøre dem **grønne**.
- Kør kun den fil, du arbejder på: `uv run pytest tests/test_cleaning.py -v`.
- Sidder du fast? 1) Læs pytests output nedefra og op. 2) Læs hintet i `TODO`.
  3) Se på slidet for det trin. 4) Kig først derefter i `solution/tests/`.

**Forudsætninger:** PostgreSQL kører, og `uv sync` fra del 1. Kør `uv sync` igen: del 4 bruger
`pytest` og `pytest-postgresql`. Del 4 kræver ikke, at del 1–3 er færdige.

---

## Forberedelse (før undervisningen, ca. 35 min)

1. Kør `uv sync` i mappen `sundhedsapp_postgres`.
2. Åbn `db.py` i denne mappe. Hvis dit password ikke er `postgres`, så ret det i `DATABASE_URL`.
   Testene bruger samme server og password, men deres egne databaser.
3. Læs [theory.md](theory.md), og besvar de otte spørgsmål under "Test dig selv".

---

> 🏠 **Trin 1–2 er en del af forberedelsen.** Lav dem hjemme, så tiden i undervisningen går til
> fixtures, databasen og login (trin 3–6).

## Trin 1: Din første test (10 min)

1. **1.1** Kør alle tests i en terminal i mappen `del4_tests`:
   ```bash
   uv run pytest
   ```
   Du ser `20 failed, 6 passed`. Det er meningen. De 6 grønne er udleveret, og de 20 røde er dine.
   💡 Første gang tager det lidt tid: pytest-postgresql laver skabelon-databasen og hasher passwords.
2. **1.2** Åbn [cleaning.py](cleaning.py) og [tests/test_cleaning.py](tests/test_cleaning.py).
   Læs `clean_name()` og `test_clean_name_capitalizes()`. Kør kun den fil med ét navn per test:
   ```bash
   uv run pytest tests/test_cleaning.py -v
   ```
3. **1.3** Skriv `test_clean_name_strips_spaces`.
4. **1.4** Skriv `test_clean_name_keeps_hyphen`. Kør filen igen.
5. **1.5 Ødelæg koden med vilje.** Fjern `.strip()` i `clean_name()` i `cleaning.py`, og kør testene.
   Læs outputtet: hvilken test fejler, og hvilke **to værdier** viser pytest? Sæt `.strip()` tilbage.

✅ **Tjek:** 1.3 og 1.4 er grønne (`PASSED`). I 1.5 viser pytest `assert '  kevin  ' == 'Kevin'`.

💡 Hvad giver `clean_name("van der berg")`? Er det rigtigt? Tests afslører de antagelser, koden har.

## Trin 2: parametrize og pytest.raises (10 min)

1. **2.1** Læs `test_clean_allergies`. Hvor mange gange kører den nu? (Se `-v`-outputtet.)
2. **2.2** Tilføj fem rækker til tabellen. Kør med `-v`, og se hver række som sin egen test.
3. **2.3** Skriv `test_clean_blood_type_normalizes`.
4. **2.4** Skriv `test_clean_blood_type_rejects_unknown` med `pytest.raises(ValueError)`.
5. **2.5** Skriv `test_clean_name_rejects_empty` med `pytest.raises(ValueError, match="tom")`.
   🔬 Prøv `match="blank"` i stedet. Hvad sker der? Sæt det tilbage.

✅ **Tjek:** `uv run pytest tests/test_cleaning.py -v` giver `13 passed`.

---

## Trin 3: Test tokens med monkeypatch (6 min)

1. **3.1** Åbn [tests/test_tokens.py](tests/test_tokens.py). Læs `test_token_roundtrip` og hjælpefunktionen
   `forge_payload`. Hvad prøver den at snyde med?
2. **3.2** Skriv `test_forged_token_is_rejected`: lav et token til bruger 2, og forfalsk det til bruger 1.
3. **3.3** Skriv `test_garbage_is_rejected`.
4. **3.4** Skriv `test_expired_token_is_rejected` med `monkeypatch.setattr(auth, "TOKEN_LIFETIME_SECONDS", -1)`.

✅ **Tjek:** `uv run pytest tests/test_tokens.py -v` giver `4 passed` på under et sekund.
Ingen database, ingen server: kun logik.

💡 Hvorfor er det vigtigt, at `monkeypatch` sætter `TOKEN_LIFETIME_SECONDS` tilbage efter testen?

## Trin 4: Test databasen med pytest-postgresql (10 min)

1. **4.1** Åbn [tests/conftest.py](tests/conftest.py), og læs afsnittet **Trin 4**. Svar på:
   - Hvilken server og hvilket password bruger testene? (Hint: `db.DATABASE_URL`.)
   - Hvad hedder testdatabasen? Hvorfor må den ikke hedde `sundhedsapp`?
   - Hvad gør `load_test_data`, og hvor mange gange kører den?
   - Hvad ændrer `db_url` med `monkeypatch`, og hvorfor?
2. **4.2** Åbn [tests/test_database.py](tests/test_database.py). Kør den. `test_all_patients` er grøn.
3. **4.3** Skriv `test_patients_of_doctor`.
4. **4.4** Skriv `test_delete_patient` med tre asserts.
5. **4.5** Skriv `test_database_is_fresh_for_each_test`. Hvorfor er der stadig 12 patienter?
6. **4.6** Skriv `test_database_rejects_bad_blood_type` med fixturen `postgresql` og `pytest.raises(CheckViolation)`.
7. **4.7** Kør `SELECT COUNT(*) FROM patient;` i **din** `sundhedsapp`-database i pgAdmin. Er den ændret?

✅ **Tjek:** `uv run pytest tests/test_database.py -v` giver `5 passed`. Din egen database er urørt.
Læg mærke til tiden: ca. 1 sekund per test, mod millisekunder i trin 1–3.

## Trin 5: Login-fixturen (8 min)

1. **5.1** I `conftest.py`, afsnit **Trin 5**: læs fixturen `client`, og skriv den indre funktion
   `_login` i fixturen `login`.
2. **5.2** Åbn [tests/test_login.py](tests/test_login.py). Skriv `test_login_wrong_password`.
3. **5.3** Skriv `test_login_unknown_user_gives_same_message`. Hvorfor er det en vigtig test? (Del 3, afsnit 4.)
4. **5.4** Skriv `test_me_without_token`.
5. **5.5** Skriv `test_me_with_token` med `headers=login("mette")`.

✅ **Tjek:** `uv run pytest tests/test_login.py -v` giver `5 passed`.

💡 Følg kæden: `test_me_with_token` beder om `login`. Hvilke fixtures bygger pytest, før testen kører?

## Trin 6: Test alle adgangsregler (6 min)

1. **6.1** Åbn [tests/test_access.py](tests/test_access.py). Skriv kroppen i `test_access` med `client.open(...)`.
2. **6.2** Tilføj de seks manglende rækker fra tabellen i del 3.
3. **6.3** Gør `test_doctor_sees_only_own_patients` færdig, og tilføj rækken for `jonas`.
4. **6.4 Lad testene fange en fejl.** I `app.py`: tilføj `"doctor"` til `roles` på `/patients`. Kør
   `uv run pytest tests/test_access.py`. Hvilken test bliver rød, og hvad siger den? Fjern `"doctor"` igen.
5. **6.5** Kør alle tests: `uv run pytest`.

✅ **Tjek:** `uv run pytest` giver `38 passed`. I 6.4 fejler præcis én test:
`test_access[GET-/patients-mette-403]` med `assert 200 == 403`.

💡 Det er den samme tabel som `client.py` i del 3. Hvad er forskellen på at se tabellen og at have den som test?

---

## Ekstra (hvis du har tid, eller hjemme)

1. **Flere adgangstests:** skriv `test_no_token_gives_401`, parametriseret over `/me`, `/patients` og
   `/my_patients`. Skriv `test_admin_can_delete_patient`: `204` første gang, `404` anden gang, og 11 patienter bagefter.
2. **Kun de fejlede:** ødelæg én ting, og kør `uv run pytest --lf`. Prøv også `-x` og `-k login`.
3. **Coverage:** hvor meget af koden kører testene? Prøv
   `uv run --with pytest-cov pytest --cov=. --cov-report=term-missing`. Hvilke linjer testes ikke?
4. **Test en ny feature først:** skriv en test til `POST /patients` (ekstraopgave 2 i del 3), *før* du
   skriver endpointet. Se den fejle, skriv koden, og se den blive grøn. Det kaldes test-driven development.
5. **Hurtigere tests:** hvorfor ville `@pytest.fixture(scope="session")` på `db_url` gøre testene hurtigere,
   men farligere? (Hint: trin 4.5.)

## Refleksion

Skriv 2–3 sætninger i dine egne noter:

- Hvilken af dagens tests ville have fanget en rigtig fejl, du selv lavede i del 1–3?
- Hvorfor tester vi rene funktioner uden database, når vi nu har en testdatabase?
- Hvad er en fixture, forklaret til en, der ikke var her i dag?

## Læs mere

Se linklisten nederst i [theory.md](theory.md#læs-mere).
