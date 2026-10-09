"""Byg del4_theory.pptx til del 4: tests med pytest, pytest-postgresql og login-fixtures.

Bygget på EK-skabelonen via kit.py. Del 4 bruger sin egen farvefamilie (use_part(4)).

Kør fra mappen sundhedsapp_postgres (luk præsentationen i PowerPoint først):

    uv run --with python-pptx slides/build_del4.py

Et valgfrit argument gemmer præsentationen et andet sted: build_del4.py other.pptx
"""

import sys
from pathlib import Path

from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN

from kit import (
    BAD, CORAL, DARK, GOOD, HEAD, MINT, MONO, MUTED, PALE_TEXT, TEAL, WARN_BG, WHITE,
    badge, card, code_box, hint_cards, new_slide, roadmap, save, section, shape, table, text, title, title_slide, use_part,
)


OUT = Path(__file__).parent.parent / "del4_tests" / "del4_theory.pptx"


# --- Intro -----------------------------------------------------------------------


def slide_title():
    title_slide('Lektion 5 · Del 4', 'Tests med pytest',
                'Rene funktioner, en frisk testdatabase og en login-fixture',
                ['assert', 'parametrize', 'fixtures', 'pytest-postgresql'],
                'Opsummering af del 3: login, tokens og roller. Vi testede reglerne ved at se på en tabel fra client.py. I dag bliver den tabel til tests, der kører automatisk.')


def slide_plan():
    s = new_slide()
    title(s, "Planen for del 4", "Trin 1–2 hjemme, trin 3–6 i undervisningen")
    columns = [
        ("Hjemme", TEAL, [
            ("P", "uv sync, password i db.py, læs theory.md"),
            ("1", "Din første test: assert"),
            ("2", "parametrize og pytest.raises"),
        ]),
        ("I undervisningen", CORAL, [
            ("3", "Tokens og monkeypatch"),
            ("4", "Databasen med pytest-postgresql"),
            ("5", "Login-fixturen"),
            ("6", "Alle adgangsregler"),
        ]),
    ]
    for c, (heading, color, steps) in enumerate(columns):
        x = 0.5 + c * 4.6
        text(s, x, 1.5, 4.3, 0.4, heading, font=HEAD, size=20, bold=True, color=color)
        for i, (label, body) in enumerate(steps):
            y = 2.0 + i * 0.6
            badge(s, x, y, label, color, size=0.42)
            text(s, x + 0.6, y, 3.8, 0.42, body, size=14, anchor=MSO_ANCHOR.MIDDLE)


def slide_why():
    s = new_slide()
    title(s, "Hvorfor automatiske tests?", "I del 3 tjekkede vi tabellen fra client.py med øjnene")
    items = [
        ("1", "Sikkerhedsnet", "Nogen ændrer roles=[...] ved en fejl. En test bliver rød med det samme."),
        ("2", "Dokumentation", "assert clean_name(\"anne-marie\") == \"Anne-Marie\" siger præcist, hvad koden gør."),
        ("3", "Mod til at ændre", "Du kan rydde op, fordi testene siger til, hvis du ødelægger noget."),
    ]
    for i, (number, heading, body) in enumerate(items):
        x = 0.5 + i * 3.05
        card(s, x, 1.65, 2.85, 2.35)
        badge(s, x + 0.25, 1.9, number, CORAL)
        text(s, x + 0.25, 2.5, 2.4, 0.45, heading, font=HEAD, size=18, bold=True, color=DARK)
        text(s, x + 0.25, 2.95, 2.4, 1.0, body, size=13)
    text(s, 0.5, 4.4, 9, 0.5, "En test er kode, der kører din kode og tjekker resultatet selv.",
         size=17, bold=True, color=TEAL)


# --- Afsnit 1: pytest -----------------------------------------------------------


def slide_anatomy():
    s = new_slide()
    title(s, "Anatomien af en test", "pytest finder selv tests ud fra navnene")
    code_box(s, 0.5, 1.45, 5.4, 1.35,
             "# tests/test_cleaning.py\n"
             "from cleaning import clean_name\n"
             "\n"
             "def test_clean_name_capitalizes() -> None:\n"
             "    assert clean_name(\"holm\") == \"Holm\"", size=12)
    table(s, 6.1, 1.45, [1.0, 2.4], [
        ["Hvad", "Regel"],
        ["Fil", "test_*.py"],
        ["Test", "def test_*():"],
        ["Tjek", "almindelig assert"],
    ], size=12, row_h=0.34, mono_cols=(1,))
    text(s, 0.5, 3.0, 9, 0.35, "Når en test fejler, viser pytest begge værdier:", font=HEAD, size=15,
         bold=True, color=DARK)
    code_box(s, 0.5, 3.4, 9.0, 0.85,
             ">       assert clean_name(\"  kevin  \") == \"Kevin\"\n"
             "E       AssertionError: assert '  kevin  ' == 'Kevin'", size=12)
    text(s, 0.5, 4.45, 9, 0.5, "Arrange, Act, Assert: gør klar, kør koden, tjek resultatet. "
         "Én ting per test, og et navn der siger hvad.", size=13, italic=True, color=MUTED)


def slide_running():
    s = new_slide()
    title(s, "Kør testene", "Alle kommandoer fra mappen del4_tests")
    table(s, 0.5, 1.45, [4.2, 3.5], [
        ["Kommando", "Gør"],
        ["uv run pytest", "alle tests i tests/"],
        ["uv run pytest -v", "ét navn per test"],
        ["uv run pytest tests/test_login.py", "kun én fil"],
        ["uv run pytest -k blood_type", "kun tests med det i navnet"],
        ["uv run pytest -x", "stop ved første fejl"],
        ["uv run pytest --lf", "kun dem, der fejlede sidst"],
    ], size=12, row_h=0.42, mono_cols=(0,))
    legend = [(".", "bestået", GOOD), ("F", "fejlet: en assert", BAD), ("E", "fejl i en fixture", CORAL)]
    for i, (mark, meaning, color) in enumerate(legend):
        y = 1.5 + i * 0.75
        badge(s, 8.45, y, mark, color, size=0.45, font_size=16)
        text(s, 8.05, y + 0.48, 1.45, 0.3, meaning, size=10, color=MUTED, align=PP_ALIGN.CENTER)


def slide_parametrize():
    s = new_slide()
    title(s, "Trin 2: parametrize", "Én test, en tabel af eksempler")
    code_box(s, 0.5, 1.45, 5.4, 2.6,
             "@pytest.mark.parametrize(\n"
             "    (\"value\", \"expected\"),\n"
             "    [\n"
             "        (False, None),\n"
             "        (\"No\", None),\n"
             "        (\"Peanuts\", \"Peanuts\"),\n"
             "    ],\n"
             ")\n"
             "def test_clean_allergies(value, expected):\n"
             "    assert clean_allergies(value) == expected", size=11)
    code_box(s, 6.1, 1.45, 3.4, 1.3,
             "test_clean_allergies[False-None]\n"
             "test_clean_allergies[No-None]\n"
             "test_clean_allergies[Peanuts-Peanuts]", size=9)
    hint_cards(s, 6.1, 2.95, 3.4, [
        ("Én række = én test", "Fejler én række, kører de andre stadig."),
    ], card_h=1.1)
    text(s, 0.5, 4.3, 9, 0.6, "Brug det, når du ellers ville kopiere den samme test med nye værdier.",
         size=14, italic=True, color=TEAL)


def slide_raises():
    s = new_slide()
    title(s, "Trin 2: pytest.raises", "Nogle gange er det rigtige svar en exception")
    code_box(s, 0.5, 1.45, 5.4, 1.1,
             "def test_clean_blood_type_rejects_unknown():\n"
             "    with pytest.raises(ValueError):\n"
             "        clean_blood_type(\"X+\")", size=12)
    code_box(s, 0.5, 2.7, 5.4, 1.1,
             "def test_clean_name_rejects_empty():\n"
             "    with pytest.raises(ValueError, match=\"tom\"):\n"
             "        clean_name(\"   \")", size=12)
    hint_cards(s, 6.1, 1.45, 3.4, [
        ("Består", "når koden i with kaster den exception."),
        ("Fejler", "når der ingen exception kommer: DID NOT RAISE."),
        ("match=", "tjekker også beskeden (regex)."),
    ], card_h=0.8, gap=0.1, body_size=12)
    text(s, 0.5, 4.1, 9, 0.8,
         [[("Virker også med databasen: ", {"bold": True, "color": DARK}),
           ("with pytest.raises(CheckViolation): ...  (trin 4.6)", {"font": MONO, "size": 12})]],
         size=14)


# --- Afsnit 2: fixtures ---------------------------------------------------------


def slide_fixtures():
    s = new_slide()
    title(s, "Fixtures: det, en test har brug for", "Skriv fixturens navn som parameter, og pytest gør resten")
    chain = [("postgresql", "frisk database"), ("db_url", "peger db.py på den"),
             ("client", "Flask test client"), ("login", "login(\"mette\") → headers")]
    for i, (name, meaning) in enumerate(chain):
        x = 0.5 + i * 2.3
        last = i == len(chain) - 1
        card(s, x, 1.5, 2.0, 1.0, DARK if last else MINT)
        text(s, x, 1.55, 2.0, 0.45, name, font=MONO, size=14, bold=True,
             color=WHITE if last else DARK, align=PP_ALIGN.CENTER)
        text(s, x + 0.05, 2.0, 1.9, 0.45, meaning, size=11, color=PALE_TEXT if last else MUTED,
             align=PP_ALIGN.CENTER)
        if not last:
            shape(s, MSO_SHAPE.RIGHT_ARROW, x + 2.04, 1.88, 0.22, 0.24, CORAL)
    code_box(s, 0.5, 2.8, 5.4, 1.5,
             "@pytest.fixture\n"
             "def client(db_url):\n"
             "    return app.test_client()\n"
             "\n"
             "def test_me_without_token(client):\n"
             "    assert client.get(\"/me\").status_code == 401", size=11)
    hint_cards(s, 6.1, 2.8, 3.4, [
        ("conftest.py", "Fixtures her kan bruges af alle tests i mappen, uden import."),
        ("Ny for hver test", "Ingen test kan ødelægge noget for den næste."),
    ], card_h=0.72, gap=0.06, body_size=11)


def slide_monkeypatch():
    s = new_slide()
    title(s, "Trin 3: monkeypatch", "En fixture fra pytest: ændr noget, men kun under testen")
    code_box(s, 0.5, 1.45, 5.6, 1.5,
             "def test_expired_token_is_rejected(monkeypatch):\n"
             "    monkeypatch.setattr(auth,\n"
             "                        \"TOKEN_LIFETIME_SECONDS\", -1)\n"
             "    token = create_token(7)\n"
             "    assert read_token(token) is None", size=11)
    code_box(s, 0.5, 3.1, 5.6, 1.1,
             "@pytest.fixture\n"
             "def db_url(postgresql, monkeypatch):\n"
             "    monkeypatch.setattr(db, \"DATABASE_URL\", url)", size=11)
    hint_cards(s, 6.35, 1.45, 3.15, [
        ("Ingen ventetid", "Vi vil ikke vente 30 minutter på, at et token udløber."),
        ("Sættes tilbage", "Efter testen har værdien sin gamle værdi igen."),
        ("Samme trick i trin 4", "db_url peger hele app'en på testdatabasen."),
    ], card_h=0.9, gap=0.1, body_size=11)


# --- Afsnit 3: databasen --------------------------------------------------------


def slide_pytest_postgresql():
    s = new_slide()
    title(s, "pytest-postgresql: en frisk database per test",
          "Din server og dit password fra db.py, men egne databaser")
    databases = [
        ("sundhedsapp", "din database: røres ikke", GOOD),
        ("sundhedsapp_test_tmpl", "skabelon: schema + data + brugere, laves én gang", TEAL),
        ("sundhedsapp_test_… (test 1)", "kopi, slettes efter testen", MUTED),
        ("sundhedsapp_test_… (test 2)", "kopi, slettes efter testen", MUTED),
    ]
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 0.5, 1.45, 9.0, 0.45, DARK, radius=0.1)
    text(s, 0.7, 1.45, 8.6, 0.45, "din PostgreSQL-server (localhost:5432)", font=HEAD, size=14,
         bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    for i, (name, meaning, color) in enumerate(databases):
        y = 2.05 + i * 0.55
        shape(s, MSO_SHAPE.RECTANGLE, 0.8, y + 0.08, 0.12, 0.3, color)
        text(s, 1.05, y, 3.8, 0.45, name, font=MONO, size=12, bold=True, color=DARK,
             anchor=MSO_ANCHOR.MIDDLE)
        text(s, 4.9, y, 4.6, 0.45, meaning, size=13, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 0.5, 4.35, 9, 0.6, "Sletter én test en patient, har den næste stadig alle 12. Det "
         "kaldes isolation, og du tester det i trin 4.5.", size=13, italic=True, color=TEAL)


def slide_conftest():
    s = new_slide()
    title(s, "Trin 4.1: conftest.py", "Tre linjer pytest-postgresql og én egen fixture")
    code_box(s, 0.5, 1.45, 5.8, 3.4,
             "postgresql_server = factories.postgresql_noproc(\n"
             "    host=..., port=..., user=..., password=...,\n"
             "    dbname=\"sundhedsapp_test\",\n"
             "    load=[load_test_data],\n"
             ")\n"
             "postgresql = factories.postgresql(\"postgresql_server\")\n"
             "\n"
             "@pytest.fixture\n"
             "def db_url(postgresql, monkeypatch) -> str:\n"
             "    info = postgresql.info\n"
             "    url = make_conninfo(host=info.host, ...)\n"
             "    monkeypatch.setattr(db, \"DATABASE_URL\", url)\n"
             "    return url", size=10)
    hint_cards(s, 6.5, 1.45, 3.0, [
        ("noproc", "Brug en server, der allerede kører. Ingen pg_ctl nødvendig."),
        ("load", "Fylder skabelonen én gang per testkørsel."),
        ("postgresql", "En psycopg-connection til testens egen kopi."),
    ], card_h=1.05, gap=0.12, body_size=11)


def slide_cost():
    s = new_slide()
    title(s, "To ting, vi lærte undervejs", "Og som du skal kende, når du tester med en database")
    hint_cards(s, 0.5, 1.45, 4.4, [
        ("Hastighed", "En frisk database koster ca. 1 sekund per test. Rene funktioner tager "
                      "millisekunder: 17 tests på 0,07 s."),
        ("Hashing én gang", "scrypt tager ca. 0,5 s per password, og det er med vilje. Brugerne "
                            "oprettes derfor i skabelonen, ikke i hver test."),
    ], card_h=1.35, gap=0.15, body_size=12)
    card(s, 5.1, 1.45, 4.4, 2.85, WARN_BG)
    text(s, 5.3, 1.55, 4.0, 0.4, "æ, ø og å på Windows", font=HEAD, size=15, bold=True, color=BAD)
    text(s, 5.3, 2.0, 4.0, 1.2,
         "pytest-postgresql åbner .sql-filer uden encoding=\"utf-8\". På Windows bliver "
         "\"Sørensen\" til \"SÃ¸rensen\", uden nogen fejl.", size=12)
    code_box(s, 5.3, 3.2, 4.0, 0.9,
             "(FOLDER / name).read_text(\n    encoding=\"utf-8\")", size=11)
    text(s, 0.5, 4.5, 9, 0.5, "Derfor har test_all_patients en assert med \"Mette Sørensen\": "
         "testen fanger fejlen, hvis den kommer tilbage.", size=13, italic=True, color=MUTED)


def slide_pyramid():
    s = new_slide()
    title(s, "Testpyramiden", "Mange hurtige tests i bunden, få langsomme i toppen")
    levels = [
        ("end-to-end: browser, rigtig server", "få", "langsomme", 3.0, CORAL),
        ("API + database (trin 4–6)", "nogle", "~1 s per test", 5.2, TEAL),
        ("rene funktioner (trin 1–3)", "mange", "~1 ms per test", 7.4, DARK),
    ]
    for i, (label, amount, speed, width, color) in enumerate(levels):
        y = 1.5 + i * 0.95
        x = 0.5 + (7.4 - width) / 2
        shape(s, MSO_SHAPE.RECTANGLE, x, y, width, 0.8, color)
        text(s, x, y, width, 0.8, label, size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER,
             anchor=MSO_ANCHOR.MIDDLE)
        text(s, 8.1, y, 1.4, 0.4, amount, size=14, bold=True, color=color)
        text(s, 8.1, y + 0.38, 1.4, 0.4, speed, size=11, color=MUTED)
    text(s, 0.5, 4.5, 9, 0.5, "Test logikken der, hvor det er billigst. Test samspillet færre steder.",
         size=14, italic=True, color=TEAL)


# --- Afsnit 4: API og login -----------------------------------------------------


def slide_test_client():
    s = new_slide()
    title(s, "Flask test client", "Send requests direkte ind i app'en, uden en server")
    code_box(s, 0.5, 1.45, 5.6, 1.9,
             "response = client.post(\n"
             "    \"/login\",\n"
             "    json={\"username\": \"mette\",\n"
             "          \"password\": \"mette-pass\"})\n"
             "response.status_code   # 200\n"
             "response.json         # {\"token\": \"eyJ...\"}", size=11)
    table(s, 0.5, 3.45, [3.4, 2.2], [
        ["Kald", "Gør"],
        ["client.get(path, headers=...)", "GET"],
        ["client.post(path, json=...)", "POST med JSON"],
        ["client.open(path, method=...)", "vilkårlig metode"],
    ], size=11, row_h=0.36, mono_cols=(0,))
    hint_cards(s, 6.35, 1.45, 3.15, [
        ("Ingen flask run", "Ingen port, ingen anden terminal."),
        ("Samme app", "Samme endpoints og regler som i del 3."),
        ("Samme database", "db_url peger den på testdatabasen."),
    ], card_h=0.9, gap=0.1, body_size=11)


def slide_login_fixture():
    s = new_slide()
    title(s, "Trin 5: login-fixturen", "En fixture, der returnerer en funktion")
    code_box(s, 0.5, 1.45, 5.8, 2.3,
             "@pytest.fixture\n"
             "def login(client):\n"
             "    def _login(username: str) -> dict[str, str]:\n"
             "        credentials = {\"username\": username,\n"
             "                       \"password\": PASSWORDS[username]}\n"
             "        response = client.post(\"/login\", json=credentials)\n"
             "        assert response.status_code == 200\n"
             "        token = response.json[\"token\"]\n"
             "        return {\"Authorization\": f\"Bearer {token}\"}\n"
             "    return _login", size=10)
    code_box(s, 0.5, 3.9, 5.8, 0.9,
             "def test_me_with_token(client, login):\n"
             "    response = client.get(\"/me\", headers=login(\"mette\"))", size=11)
    hint_cards(s, 6.5, 1.45, 3.0, [
        ("Hvorfor en funktion?", "Samme test kan logge ind som admin, mette og nina."),
        ("Skrevet én gang", "Alle tests af beskyttede endpoints bruger den."),
        ("PASSWORDS", "Bygget ud fra TEST_USERS i users.py."),
    ], card_h=1.0, gap=0.12, body_size=11)


def slide_access():
    s = new_slide()
    title(s, "Trin 6: tabellen fra del 3 som én test", "parametrize + login-fixture")
    code_box(s, 0.5, 1.45, 5.8, 3.3,
             "@pytest.mark.parametrize(\n"
             "    (\"method\", \"path\", \"username\", \"expected\"),\n"
             "    [\n"
             "        (\"GET\", \"/patients\", \"admin\", 200),\n"
             "        (\"GET\", \"/patients\", \"nina\", 200),\n"
             "        (\"GET\", \"/patients\", \"mette\", 403),\n"
             "        ...\n"
             "    ],\n"
             ")\n"
             "def test_access(client, login, method, path,\n"
             "                username, expected):\n"
             "    response = client.open(path, method=method,\n"
             "                           headers=login(username))\n"
             "    assert response.status_code == expected", size=10)
    hint_cards(s, 6.5, 1.45, 3.0, [
        ("9 rækker", "/patients, /my_patients og DELETE for tre brugere."),
        ("6.4 bryd en regel", "Giv doctor adgang til /patients. Én test bliver rød."),
    ], card_h=1.05, gap=0.15, body_size=11)
    code_box(s, 6.5, 3.85, 3.0, 0.9,
             "FAILED test_access[GET-\n/patients-mette-403]\nassert 200 == 403", size=9)


# --- Afsnit 5: sådan løser du trinene --------------------------------------------


def slide_step3():
    s = new_slide()
    title(s, "Trin 3: tokens", "Ren logik: ingen database, ingen server, under et sekund")
    code_box(s, 0.5, 1.45, 5.6, 2.9,
             "def test_forged_token_is_rejected():\n"
             "    forged = forge_payload(create_token(2), 1)\n"
             "    assert read_token(forged) is None\n"
             "\n"
             "def test_garbage_is_rejected():\n"
             "    assert read_token(\"ikke et token\") is None\n"
             "\n"
             "def test_expired_token_is_rejected(monkeypatch):\n"
             "    monkeypatch.setattr(auth, \"TOKEN_LIFETIME_SECONDS\", -1)\n"
             "    assert read_token(create_token(7)) is None", size=10)
    hint_cards(s, 6.35, 1.45, 3.15, [
        ("forge_payload", "Mette prøver at gøre sig selv til bruger 1 (admin)."),
        ("import auth", "monkeypatch skal have modulet, ikke kun funktionen."),
        ("✅ Tjek", "4 passed på under et sekund."),
    ], card_h=0.95, gap=0.1, body_size=11)


def slide_step4():
    s = new_slide()
    title(s, "Trin 4: tests mod databasen", "Bed om db_url, og kald funktionerne som normalt")
    code_box(s, 0.5, 1.45, 5.6, 3.3,
             "def test_patients_of_doctor(db_url):\n"
             "    names = [p[\"first_name\"] for p in patients_of_doctor(1)]\n"
             "    assert names == [\"Kevin\", \"Karen\", \"Erik\"]\n"
             "\n"
             "def test_delete_patient(db_url):\n"
             "    assert delete_patient(1) is True\n"
             "    assert delete_patient(1) is False\n"
             "    assert len(all_patients()) == 11\n"
             "\n"
             "def test_database_rejects_bad_blood_type(postgresql):\n"
             "    with pytest.raises(CheckViolation):\n"
             "        postgresql.execute(\"INSERT ... 'X+' ...\")", size=10)
    hint_cards(s, 6.35, 1.45, 3.15, [
        ("db_url", "Din kode bruger testdatabasen."),
        ("postgresql", "Rå SQL direkte mod testdatabasen."),
        ("4.5 isolation", "Efter delete har næste test stadig 12."),
        ("4.7 pgAdmin", "Din sundhedsapp er urørt."),
    ], card_h=0.75, gap=0.08, body_size=11)


def slide_step5():
    s = new_slide()
    title(s, "Trin 5: test login", "Samme besked for forkert password og ukendt bruger")
    code_box(s, 0.5, 1.45, 5.6, 1.5,
             "def test_login_wrong_password(client):\n"
             "    response = client.post(\"/login\", json={\n"
             "        \"username\": \"mette\", \"password\": \"forkert\"})\n"
             "    assert response.status_code == 401\n"
             "    assert response.json[\"message\"] == WRONG_LOGIN", size=10)
    code_box(s, 0.5, 3.1, 5.6, 1.3,
             "def test_me_with_token(client, login):\n"
             "    response = client.get(\"/me\", headers=login(\"mette\"))\n"
             "    assert response.status_code == 200\n"
             "    assert response.json == {\"username\": \"mette\",\n"
             "                             \"role\": \"doctor\"}", size=10)
    hint_cards(s, 6.35, 1.45, 3.15, [
        ("5.1 først", "Uden login-fixturen fejler 5.5 og hele trin 6."),
        ("5.3 hvorfor?", "En anden besked afslører, hvilke brugernavne der findes."),
        ("✅ Tjek", "5 passed"),
    ], card_h=0.9, gap=0.1, body_size=11)


def slide_errors():
    s = new_slide()
    title(s, "Almindelige fejl og hvad de betyder")
    table(s, 0.5, 1.2, [4.6, 4.4], [
        ["Du ser", "Det betyder"],
        ["F … NotImplementedError: trin 2.3", "godt! Skriv den test"],
        ["E … password authentication failed", "forkert password i db.py"],
        ["E … Connection refused", "PostgreSQL-servicen kører ikke"],
        ["fixture 'login' not found", "stavefejl, eller conftest.py ligger forkert"],
        ["DID NOT RAISE <class 'ValueError'>", "koden kastede ingen exception"],
        ["assert 403 == 200", "app'en svarede 403, testen forventede 200"],
        ["No module named 'pytest_postgresql'", "kør uv sync"],
    ], size=11, row_h=0.45, mono_cols=(0,))


def slide_links():
    s = new_slide()
    title(s, "Læs mere", "Alle links står også nederst i theory.md")
    groups = [
        ("pytest", [
            ("Get started", "https://docs.pytest.org/en/stable/getting-started.html"),
            ("Assertions og raises", "https://docs.pytest.org/en/stable/how-to/assert.html"),
            ("parametrize", "https://docs.pytest.org/en/stable/how-to/parametrize.html"),
            ("Fixtures", "https://docs.pytest.org/en/stable/how-to/fixtures.html"),
            ("monkeypatch", "https://docs.pytest.org/en/stable/how-to/monkeypatch.html"),
        ]),
        ("Database og API", [
            ("pytest-postgresql", "https://github.com/dbfixtures/pytest-postgresql"),
            ("Template databases",
             "https://www.postgresql.org/docs/current/manage-ag-templatedbs.html"),
            ("Flask: testing", "https://flask.palletsprojects.com/en/stable/testing/"),
        ]),
        ("Strategi", [
            ("Real Python: pytest", "https://realpython.com/pytest-python-testing/"),
            ("Fowler: test pyramid",
             "https://martinfowler.com/articles/practical-test-pyramid.html"),
        ]),
    ]
    for i, (heading, links) in enumerate(groups):
        x = 0.5 + i * 3.05
        card(s, x, 1.45, 2.85, 3.0)
        text(s, x + 0.2, 1.6, 2.5, 0.35, heading, font=HEAD, size=16, bold=True, color=DARK)
        lines_ = [[(label, {"color": TEAL, "link": url})] for label, url in links]
        text(s, x + 0.2, 2.05, 2.5, 3.0, lines_, size=13, space_after=7)


def slide_roadmap():
    roadmap('Din tur: exercise.md, trin 3–6', [
        ('3', 'Tokens', 'monkeypatch', 6),
        ('4', 'Database', 'db_url + postgresql', 10),
        ('5', 'Login', 'login-fixture', 8),
        ('6', 'Adgang', 'parametrize', 6),
    ], [
        [('Kør kun din fil: ', {"bold": True, "color": DARK}),
         ('uv run pytest tests/test_database.py '
          '-v', {"font": MONO})],
        [('Sidder du fast? ', {"bold": True, "color": DARK}),
         ('1) læs pytests output nedefra og op  2) læs TODO-hintet  3) '
          'find slidet for trinnet  4) kig i solution/tests/', {})],
        [('Færdig før tid? ', {"bold": True, "color": DARK}),
         ('Ekstraopgaver: flere adgangstests, --lf, coverage, '
          'test-driven development.', {})],
    ])


def main() -> None:
    use_part(4)
    slide_title()
    slide_plan()
    slide_why()
    section(1, "pytest: det grundlæggende", "assert, parametrize og pytest.raises (trin 1–2)")
    slide_anatomy()
    slide_running()
    slide_parametrize()
    slide_raises()
    section(2, "Fixtures", "Det, en test har brug for, og monkeypatch (trin 3)")
    slide_fixtures()
    slide_monkeypatch()
    section(3, "Test med en rigtig database", "pytest-postgresql (trin 4)")
    slide_pytest_postgresql()
    slide_conftest()
    slide_cost()
    slide_pyramid()
    section(4, "Test API'et og login", "Flask test client og login-fixturen (trin 5–6)")
    slide_test_client()
    slide_login_fixture()
    slide_access()
    section(5, "Sådan løser du trin 3–6", "Mønstre, hints og de tjek, du skal kigge efter")
    slide_step3()
    slide_step4()
    slide_step5()
    slide_errors()
    slide_links()
    slide_roadmap()
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else OUT
    try:
        save(out, "Del 4 - Tests med pytest")
    except PermissionError:
        sys.exit(f"Kan ikke skrive {out}. Luk den i PowerPoint, og kør igen.")
    print(f"skrev {out}")


if __name__ == "__main__":
    main()
