# Del 4 – Teori: tests med pytest, pytest-postgresql og login-fixtures

Læs dette før undervisningen (ca. 35 minutter). Slides'ene `del4_theory.pptx` dækker de samme
emner og viser, hvordan du løser hvert trin i øvelsen.

---

## 1. Hvorfor automatiske tests?

I del 3 testede du adgangsreglerne ved at klikke rundt i `/docs` og ved at køre `client.py` og
sammenligne en tabel med øjnene. Det virker én gang. Men hver gang nogen ændrer koden, skal det
gøres igen, og en dag glemmer man det.

En **automatisk test** er kode, der kører din kode og **tjekker resultatet selv**:

- **Sikkerhedsnet:** ændrer nogen `roles=["admin", "nurse"]` til `roles=["admin"]`, bliver en test
  rød med det samme, og ikke først når en sygeplejerske ringer.
- **Dokumentation:** `assert clean_name("anne-marie") == "Anne-Marie"` forklarer præcist, hvad
  funktionen gør.
- **Mod til at ændre:** du kan rydde op i koden, fordi testene fortæller dig, hvis du ødelægger noget.

## 2. pytest: det grundlæggende

pytest finder selv dine tests efter en simpel navneregel:

| Hvad | Regel | Eksempel |
|---|---|---|
| Fil | starter med `test_` | `tests/test_cleaning.py` |
| Test | funktion, der starter med `test_` | `def test_clean_name_capitalizes():` |
| Tjek | helt almindelig `assert` | `assert clean_name("holm") == "Holm"` |

```python
from cleaning import clean_name

def test_clean_name_capitalizes() -> None:
    assert clean_name("holm") == "Holm"
```

Når en `assert` fejler, viser pytest **begge værdier**, så du kan se, hvad der gik galt:

```
>       assert clean_name("  kevin  ") == "Kevin"
E       AssertionError: assert '  kevin  ' == 'Kevin'
```

### Arrange, Act, Assert

En god test har tre dele, ofte bare én linje hver:

```python
def test_delete_patient(db_url):
    # Arrange: databasen har 12 patienter (klaret af fixturen)
    # Act
    deleted = delete_patient(1)
    # Assert
    assert deleted is True
```

Test **én ting** per test, og giv testen et navn, der siger hvad: `test_login_wrong_password`,
ikke `test_login_2`.

### Kør testene

| Kommando | Gør |
|---|---|
| `uv run pytest` | kør alle tests i `tests/` |
| `uv run pytest -v` | ét navn per test (verbose) |
| `uv run pytest tests/test_login.py` | kun én fil |
| `uv run pytest -k blood_type` | kun tests med `blood_type` i navnet |
| `uv run pytest -x` | stop ved første fejl |
| `uv run pytest --lf` | kør kun dem, der fejlede sidst (*last failed*) |

`.` = bestået, `F` = fejlet, `E` = fejl i opsætningen (en fixture fejlede).

## 3. parametrize: én test, mange eksempler

I stedet for at kopiere samme test fem gange giver du en tabel af input og forventet output:

```python
@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (False, None),
        ("No", None),
        ("Peanuts", "Peanuts"),
    ],
)
def test_clean_allergies(value, expected):
    assert clean_allergies(value) == expected
```

pytest kører testen én gang per række og viser hver som sin egen test:
`test_clean_allergies[False-None]`, `test_clean_allergies[No-None]` … Fejler én række, kører de andre stadig.

## 4. pytest.raises: test, at noget fejler

Nogle gange er det **rigtige** resultat en exception. `clean_blood_type("X+")` skal kaste
`ValueError`:

```python
def test_clean_blood_type_rejects_unknown():
    with pytest.raises(ValueError):
        clean_blood_type("X+")
```

Testen **består**, hvis koden inde i `with` kaster en `ValueError`, og **fejler**, hvis den ikke gør.
Med `match="tom"` tjekker du også, at beskeden indeholder ordet "tom".

Det virker med alle exceptions, også databasens:

```python
with pytest.raises(CheckViolation):
    postgresql.execute("INSERT INTO patient (...) VALUES (..., 'X+', 1)")
```

## 5. Fixtures: det, en test har brug for

En **fixture** gør noget klar til en test: en database, en bruger, en test client. Testen beder om
den ved at **skrive dens navn som parameter**, og pytest sørger for resten:

```python
@pytest.fixture
def client(db_url):
    return app.test_client()

def test_me_without_token(client):          # pytest kalder client() og giver dig resultatet
    assert client.get("/me").status_code == 401
```

- Fixtures kan **bruge andre fixtures**. Vores kæde er
  `postgresql` → `db_url` → `client` → `login`. Beder en test om `login`, bygger pytest hele kæden.
- **`conftest.py`**: fixtures i denne fil kan bruges af alle tests i mappen uden `import`.
- En fixture køres **på ny for hver test** (standard). Ingen test kan ødelægge noget for den næste.
- En fixture kan returnere en **funktion**. Vores `login`-fixture returnerer `login(username)`, så
  en test kan logge ind som forskellige brugere.

### monkeypatch: ændr noget midlertidigt

`monkeypatch` er en fixture, der følger med pytest. Den ændrer en værdi **kun under testen** og
sætter den tilbage bagefter:

```python
def test_expired_token_is_rejected(monkeypatch):
    monkeypatch.setattr(auth, "TOKEN_LIFETIME_SECONDS", -1)   # tokens udløber med det samme
    token = create_token(7)
    assert read_token(token) is None
```

Vi bruger den også til at pege `db.DATABASE_URL` på testdatabasen (se afsnit 6).

## 6. Test med en rigtig database: pytest-postgresql

Tests, der skriver til databasen, må **aldrig** røre dine rigtige data, og de skal starte fra
**samme udgangspunkt** hver gang. Ellers afhænger resultatet af, hvilke tests der kørte før.

**pytest-postgresql** løser det. Vi bruger den i *noproc*-tilstand: den bruger din
PostgreSQL-server (password fra `db.py`), men laver sine **egne databaser**:

```
din server
├── sundhedsapp                 ← din database, røres ikke
├── sundhedsapp_test_tmpl       ← skabelon: schema.sql + data.sql + brugere, laves én gang
├── sundhedsapp_test_…          ← kopi til test 1, slettes bagefter
└── sundhedsapp_test_…          ← kopi til test 2, slettes bagefter
```

I `conftest.py`:

```python
postgresql_server = factories.postgresql_noproc(
    host=..., port=..., user=..., password=...,   # fra db.DATABASE_URL
    dbname="sundhedsapp_test",
    load=[load_test_data],                        # fylder skabelonen én gang
)
postgresql = factories.postgresql("postgresql_server")   # én frisk kopi per test
```

- **`postgresql`** er en fixture, der giver en almindelig psycopg-connection til testens kopi.
- **`db_url`** er vores egen fixture. Den bruger `monkeypatch` til at sætte `db.DATABASE_URL` til
  kopien, så `all_patients()`, `create_users()` og hele Flask-app'en bruger testdatabasen.
- **Isolation:** sletter én test en patient, har den næste stadig alle 12. Det tester du i trin 4.5.

**Hvorfor ikke bare SQL-filer i `load`?** pytest-postgresql kan selv køre `.sql`-filer, men den åbner
dem uden `encoding="utf-8"`. På Windows bliver "Sørensen" så til "SÃ¸rensen" uden nogen fejlbesked.
Vores `load_test_data()` læser filerne som UTF-8 og opretter samtidig brugerne, så passwords kun
skal hashes én gang (scrypt er langsom med vilje: ca. 0,5 sekund per password).

> 💡 En frisk database koster ca. 1 sekund per test. Derfor tester vi rene funktioner (trin 1–3)
> **uden** database: de tager millisekunder.

## 7. Test API'et: Flask test client og login-fixturen

Flask kan køre app'en **uden en server**. `app.test_client()` giver et objekt, der sender requests
direkte ind i app'en:

```python
response = client.post("/login", json={"username": "mette", "password": "mette-pass"})
response.status_code    # 200
response.json           # {"token": "eyJ..."}
```

Næsten alle tests af beskyttede endpoints skal først logge ind. Den kode skriver vi **én gang**, i en
fixture:

```python
@pytest.fixture
def login(client):
    def _login(username):
        response = client.post("/login", json={"username": username, "password": PASSWORDS[username]})
        assert response.status_code == 200
        return {"Authorization": f"Bearer {response.json['token']}"}
    return _login

def test_me_with_token(client, login):
    response = client.get("/me", headers=login("mette"))
    assert response.json == {"username": "mette", "role": "doctor"}
```

Kombinér med `parametrize`, og tabellen fra del 3 bliver til én test med ni rækker:

```python
@pytest.mark.parametrize(("method", "path", "username", "expected"), [
    ("GET", "/patients", "nina", 200),
    ("GET", "/patients", "mette", 403),
    ...
])
def test_access(client, login, method, path, username, expected):
    response = client.open(path, method=method, headers=login(username))
    assert response.status_code == expected
```

## 8. Testpyramiden

```
          /\          få:     end-to-end (browser, rigtig server)       langsomme
         /  \
        /----\        nogle:  API + database (trin 4–6)                 ~1 s per test
       /      \
      /--------\      mange:  rene funktioner (trin 1–3)                ~1 ms per test
```

Skriv mange små, hurtige tests af logikken, og færre, langsommere tests af, at delene hænger
sammen. Vores testsuite følger pyramiden: 17 tests uden database, der tager under et sekund, og
resten med database.

---

### Test dig selv

1. Hvordan finder pytest dine tests? Hvad skal filer og funktioner hedde?
2. Hvad er forskellen på `F` og `E` i pytests output?
3. Hvornår vil du bruge `parametrize` i stedet for flere tests?
4. Hvordan tester du, at en funktion kaster en `ValueError`?
5. Hvordan får en test adgang til en fixture? Hvor skal fixturen stå, hvis mange filer skal bruge den?
6. Hvad gør `monkeypatch`, når testen er færdig?
7. Hvorfor får hver test sin egen kopi af databasen? Hvad koster det?
8. Hvorfor er `login` en fixture, der returnerer en funktion, og ikke bare et token?

---

## Læs mere

**pytest**
- [pytest: Get started](https://docs.pytest.org/en/stable/getting-started.html)
- [pytest: How to write and report assertions](https://docs.pytest.org/en/stable/how-to/assert.html). Inkl. `pytest.raises`.
- [pytest: How to parametrize](https://docs.pytest.org/en/stable/how-to/parametrize.html)
- [pytest: How to use fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html). Inkl. `conftest.py` og "factories as fixtures".
- [pytest: How to monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)
- [pytest: Usage and invocations](https://docs.pytest.org/en/stable/how-to/usage.html). `-k`, `-x`, `--lf`.
- [Real Python: Effective Python testing with pytest](https://realpython.com/pytest-python-testing/)

**Database og API**
- [pytest-postgresql (GitHub)](https://github.com/dbfixtures/pytest-postgresql). Se "Using an existing PostgreSQL server" (noproc).
- [PostgreSQL: Template databases](https://www.postgresql.org/docs/current/manage-ag-templatedbs.html). Sådan kopieres skabelonen.
- [Flask: Testing Flask applications](https://flask.palletsprojects.com/en/stable/testing/). `test_client()` og `response.json`.
- [APIFlask: Testing](https://apiflask.com/usage/#test-your-application)

**Teststrategi**
- [Martin Fowler: The practical test pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
