"""Byg del3_theory.pptx til del 3: login, passwords, tokens og role-based access control.

Bygget på EK-skabelonen via kit.py. Del 3 bruger sin egen farvefamilie (use_part(3)).

Kør fra mappen sundhedsapp_postgres (luk præsentationen i PowerPoint først):

    uv run --with python-pptx slides/build_del3.py

Et valgfrit argument gemmer præsentationen et andet sted: build_del3.py other.pptx
"""

import sys
from pathlib import Path

from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN

from kit import (
    BAD, CORAL, DARK, GOOD, HEAD, INK, MINT, MONO, MUTED, PALE_TEXT, TEAL, WHITE,
    arrow, badge, card, code_box, entity, hint_cards, line, new_slide, notes, one_to_many,
    roadmap, save, section, shape, table, text, title, title_slide, use_part, warning,
)


OUT = Path(__file__).parent.parent / "del3_login" / "del3_theory.pptx"


# --- Helpers ---------------------------------------------------------------------


def one_to_one(slide, left_x, right_x, y):
    """Linje med o| i begge ender: nul eller én på hver side."""
    line(slide, left_x, y, right_x, y)
    for bar_x in (left_x + 0.13, right_x - 0.13):
        line(slide, bar_x, y - 0.12, bar_x, y + 0.12)
    for circle_x in (left_x + 0.2, right_x - 0.34):
        shape(slide, MSO_SHAPE.OVAL, circle_x, y - 0.07, 0.14, 0.14, WHITE, line=DARK,
              line_width=1.5)


def pill(slide, x, y, w, h, label, fill, color=WHITE, size=12, font=MONO):
    shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill, radius=0.12)
    text(slide, x, y, w, h, label, font=font, size=size, bold=True, color=color,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


# --- Intro -----------------------------------------------------------------------


def slide_title():
    title_slide('Lektion 5 · Del 3', 'Login og roller',
                'Hashede passwords, JWT bearer tokens og role-based access control',
                ['app_user + role', 'Password hash', 'JWT + exp', 'roles=[...]'],
                'Opsummering af del 2: hospital, doctor og patient med foreign keys. I dag får appen brugere, der skal logge ind, og roller, der bestemmer, hvad de må.')


def slide_plan():
    s = new_slide()
    title(s, "Planen for del 3", "Trin 1–3 hjemme, trin 4–7 i undervisningen")
    columns = [
        ("Hjemme", TEAL, [
            ("P", "uv sync, læs theory.md"),
            ("1", "ER diagram: app_user og role"),
            ("2", "CREATE TABLE + roller"),
            ("3", "Hash passwords, opret brugere"),
        ]),
        ("I undervisningen", CORAL, [
            ("4", "POST /login"),
            ("5", "Tjek tokenet: verify_token"),
            ("6", "Roller: roles=[...]"),
            ("7", "Test alle regler med client.py"),
        ]),
    ]
    for c, (heading, color, steps) in enumerate(columns):
        x = 0.5 + c * 4.6
        text(s, x, 1.5, 4.3, 0.4, heading, font=HEAD, size=20, bold=True, color=color)
        for i, (label, body) in enumerate(steps):
            y = 2.0 + i * 0.6
            badge(s, x, y, label, color, size=0.42)
            text(s, x + 0.6, y, 3.8, 0.42, body, size=14, anchor=MSO_ANCHOR.MIDDLE)


def slide_problem():
    s = new_slide()
    title(s, "Problemet i lektion 4", "POST /token/1 → et token. Uden password.")
    code_box(s, 0.5, 1.45, 4.4, 0.9,
             "POST /token/1\n→ {\"token\": \"Bearer eyJ...\"}", size=13)
    hint_cards(s, 0.5, 2.5, 4.4, [
        ("Intet password", "Alle, der kan gætte tallet 1, får et gyldigt token."),
        ("Token = adgang til alt", "Ingen forskel på læge, sygeplejerske og admin."),
    ], card_h=0.9, gap=0.12)
    kinds = [
        ("Authentication", "Hvem er du?", "401 Unauthorized", "log ind"),
        ("Authorization", "Hvad må du?", "403 Forbidden", "at logge ind igen hjælper ikke"),
    ]
    for i, (name, question, code, hint) in enumerate(kinds):
        y = 1.45 + i * 1.6
        card(s, 5.1, y, 4.4, 1.45, DARK)
        text(s, 5.3, y + 0.1, 4.0, 0.4, name, font=HEAD, size=18, bold=True, color=WHITE)
        text(s, 5.3, y + 0.5, 4.0, 0.35, question, size=15, italic=True, color=PALE_TEXT)
        text(s, 5.3, y + 0.9, 4.0, 0.4, [[(code, {"font": MONO, "bold": True, "color": WHITE}),
                                          (f"  {hint}", {"color": PALE_TEXT})]], size=12)


# --- Afsnit 1: brugere og roller ----------------------------------------------------


def slide_erd():
    s = new_slide()
    title(s, "ER diagrammet: brugere og roller", "To nye tabeller. doctor, hospital og patient er fra del 2.")
    entity(s, 0.5, 1.45, 2.4, "role", [
        ("PK", "role_id", "integer"),
        ("", "role_name", "text"),
    ])
    entity(s, 3.8, 1.45, 2.4, "app_user", [
        ("PK", "user_id", "integer"),
        ("", "username", "text"),
        ("", "password_hash", "text"),
        ("FK", "role_id", "integer"),
        ("FK", "doctor_id", "int·null"),
    ])
    entity(s, 7.1, 1.45, 2.4, "doctor", [
        ("PK", "doctor_id", "integer"),
        ("", "doctor_name", "text"),
        ("FK", "hospital_id", "integer"),
        ("", "…", ""),
    ])
    one_to_many(s, 2.9, 3.8, 1.67)
    one_to_one(s, 6.2, 7.1, 1.67)
    text(s, 0.5, 2.75, 2.4, 1.2, "En rolle har mange brugere. En bruger har én rolle.",
         size=12, italic=True, color=MUTED)
    text(s, 7.1, 3.35, 2.4, 1.0, "En læge har højst én bruger. Admin og nurse har ingen læge.",
         size=12, italic=True, color=MUTED)
    warning(s, 4.4, "UNIQUE + FK = one-to-one. ",
            "doctor_id er UNIQUE, så to brugere kan ikke være samme læge.", h=0.6)


def slide_app_user_sql():
    s = new_slide()
    title(s, "Trin 2: role og app_user i SQL")
    code_box(s, 0.5, 1.2, 5.6, 3.1,
             "CREATE TABLE role (\n"
             "  role_id   INTEGER GENERATED ALWAYS\n"
             "            AS IDENTITY PRIMARY KEY,\n"
             "  role_name TEXT NOT NULL UNIQUE\n"
             ");\n"
             "INSERT INTO role (role_name)\n"
             "VALUES ('admin'), ('doctor'), ('nurse');\n"
             "\n"
             "CREATE TABLE app_user (\n"
             "  user_id  ... PRIMARY KEY,\n"
             "  username TEXT NOT NULL UNIQUE,\n"
             "  password_hash TEXT NOT NULL,\n"
             "  role_id  INTEGER NOT NULL REFERENCES role,\n"
             "  doctor_id INTEGER UNIQUE REFERENCES doctor\n"
             ");", size=10)
    hint_cards(s, 6.35, 1.2, 3.15, [
        ("Hvorfor ikke user?", "USER er reserveret: SELECT user; giver database-brugerens navn."),
        ("Hvorfor en role-tabel?", "FK'en afviser 'admn'. En tekstkolonne ville tage alt."),
        ("NULL og UNIQUE", "Flere NULL er tilladt: NULL er ikke lig med noget."),
    ], card_h=0.98, gap=0.08, body_size=11)


def slide_hashing():
    s = new_slide()
    title(s, "Gem aldrig passwords: gem et hash", "En envejsfunktion: nem at regne frem, umulig at regne tilbage")
    pill(s, 0.5, 1.5, 2.0, 0.6, "\"mette-pass\"", MINT, color=DARK)
    arrow(s, 2.65, 1.66)
    pill(s, 3.1, 1.5, 3.0, 0.6, "generate_password_hash", TEAL, size=11)
    arrow(s, 6.25, 1.66)
    pill(s, 6.7, 1.5, 2.8, 0.6, "scrypt:…$salt$hash", DARK, size=11)
    parts = [
        ("scrypt:32768:8:1", "algoritme og hvor dyr den er", DARK),
        ("jK0yzOuzAAhOfY4R", "salt: tilfældig, ny hver gang", CORAL),
        ("651b38ea62a3…", "selve hashet", TEAL),
    ]
    for i, (value, meaning, color) in enumerate(parts):
        x = 0.5 + i * 3.05
        text(s, x, 2.5, 2.85, 0.35, value, font=MONO, size=13, bold=True, color=color)
        text(s, x, 2.85, 2.85, 0.35, meaning, size=13)
    text(s, 0.5, 3.4, 9, 0.9,
         [[("Hvorfor? ", {"bold": True, "color": DARK}),
           ("Databaser bliver lækket, og folk genbruger passwords. Et læk fra din app må ikke åbne "
            "deres e-mail og netbank.", {})]], size=14)
    warning(s, 4.4, "Aldrig hashlib.sha256(password): ",
            "den er lynhurtig og uden salt. Brug en password-funktion: scrypt, argon2 eller bcrypt.",
            h=0.6)


def slide_salt():
    s = new_slide()
    title(s, "Trin 3.1: salt i praksis", "Samme password, to forskellige hashes. Begge passer.")
    code_box(s, 0.5, 1.45, 5.6, 2.75,
             ">>> h1 = generate_password_hash(\"mette-pass\")\n"
             ">>> h2 = generate_password_hash(\"mette-pass\")\n"
             ">>> h1 == h2\n"
             "False\n"
             ">>> check_password_hash(h1, \"mette-pass\")\n"
             "True\n"
             ">>> check_password_hash(h2, \"mette-pass\")\n"
             "True\n"
             ">>> check_password_hash(h1, \"Mette-pass\")\n"
             "False", size=11)
    hint_cards(s, 6.35, 1.45, 3.15, [
        ("Hvordan kan login virke?", "check_password_hash læser salt fra hashet og regner igen."),
        ("Hvad vinder vi?", "Ingen kan se, at to brugere har samme password."),
        ("Langsom med vilje", "Én login mærker det ikke. Milliarder af gæt gør."),
    ], card_h=0.9, gap=0.1, body_size=11)
    text(s, 0.5, 4.4, 9, 0.6, "Trin 3.2: create_users() hasher hvert password, før det indsættes "
         "med executemany().", size=14, italic=True, color=TEAL)


# --- Afsnit 2: login og tokens ------------------------------------------------------


def slide_flow():
    s = new_slide()
    title(s, "Login-flowet", "Log ind én gang, og send tokenet med ved hver request")
    lanes = [("klient", 0.5), ("server (Flask)", 3.9), ("database", 7.4)]
    for label, x in lanes:
        pill(s, x, 1.35, 2.1, 0.45, label, DARK, font=HEAD, size=13)
        line(s, x + 1.05, 1.8, x + 1.05, 4.95, color=MUTED, width=1)
    steps = [
        (1.95, 1.55, 4.95, "POST /login {username, password}", TEAL),
        (2.35, 4.95, 8.45, "get_user_by_username()", MUTED),
        (2.75, 4.95, 1.55, "{\"token\": \"eyJ...\"}", GOOD),
        (3.45, 1.55, 4.95, "GET /patients (Bearer eyJ...)", TEAL),
        (3.85, 4.95, 8.45, "verify_token() → get_user()", MUTED),
        (4.45, 4.95, 1.55, "200 [...]   eller   401 / 403", CORAL),
    ]
    for y, x1, x2, label, color in steps:
        line(s, x1, y + 0.3, x2, y + 0.3, color=color, width=2)
        left = min(x1, x2)
        text(s, left + 0.1, y, abs(x2 - x1) - 0.2, 0.3, label, font=MONO, size=10, color=INK,
             align=PP_ALIGN.CENTER)
    notes(s, "Samme fejlbesked for forkert brugernavn og forkert password, ellers kan en angriber "
             "finde ud af, hvilke brugernavne der findes.")


def slide_jwt():
    s = new_slide()
    title(s, "JSON Web Token (JWT)", "Tre base64-dele adskilt af punktum")
    parts = [
        ("header", "{\"alg\": \"HS256\"}", TEAL),
        ("payload", "{\"sub\": \"2\",\n \"exp\": 1791...}", CORAL),
        ("signatur", "HMAC(header.payload,\n     SECRET_KEY)", DARK),
    ]
    for i, (name, content, color) in enumerate(parts):
        x = 0.5 + i * 3.05
        pill(s, x, 1.45, 2.85, 0.45, name, color, font=HEAD, size=14)
        code_box(s, x, 2.0, 2.85, 0.9, content, size=11)
    table(s, 0.5, 3.1, [1.0, 4.0, 1.8], [
        ["Claim", "Betydning", "Hos os"],
        ["sub", "subject: hvem tokenet handler om", "user_id"],
        ["exp", "udløbstid, sekunder siden 1970", "nu + 30 min"],
    ], size=12, row_h=0.38, mono_cols=(0,))
    hint_cards(s, 7.5, 3.1, 2.0, [
        ("Ikke krypteret!", "Alle kan læse payload. Ingen hemmeligheder i den."),
    ], card_h=1.14, body_size=11)
    text(s, 0.5, 4.4, 9, 0.6, "Ændrer nogen ét tegn i payload, passer signaturen ikke → 401. Kun "
         "serveren kender SECRET_KEY, så kun den kan lave gyldige tokens.", size=13, italic=True,
         color=MUTED)


def slide_joserfc():
    s = new_slide()
    title(s, "Tokens med joserfc", "Efterfølgeren til authlib.jose fra lektion 4 (samme forfatter)")
    code_box(s, 0.5, 1.45, 5.6, 2.6,
             "def create_token(user_id: int) -> str:\n"
             "    payload = {\"sub\": str(user_id),\n"
             "               \"exp\": int(time.time()) + 30 * 60}\n"
             "    return jwt.encode({\"alg\": \"HS256\"}, payload,\n"
             "                      SECRET_KEY)\n"
             "\n"
             "def read_token(token: str) -> int | None:\n"
             "    try:\n"
             "        claims = jwt.decode(token, SECRET_KEY).claims\n"
             "        REQUIRED_CLAIMS.validate(claims)   # exp\n"
             "    except JoseError:\n"
             "        return None\n"
             "    return int(claims[\"sub\"])", size=10)
    hint_cards(s, 6.35, 1.45, 3.15, [
        ("Rollen er ikke i tokenet", "Vi slår brugeren op ved hver request. En ændret rolle virker med det samme."),
        ("SECRET_KEY", "Ny ved hver genstart: alle gamle tokens bliver ugyldige."),
        ("\"Bearer \"", "Nu skriver klienten det, ikke serveren. /docs gør det for dig."),
    ], card_h=0.98, gap=0.08, body_size=11)
    text(s, 0.5, 4.25, 5.6, 0.7, "create_token og read_token er færdige i auth.py. Læs dem, før "
         "du skriver verify_token.", size=13, italic=True, color=TEAL)


def slide_auth_required():
    s = new_slide()
    title(s, "Hvad sker der ved @app.auth_required?", "APIFlask kalder dine funktioner i denne rækkefølge")
    steps = [
        ("Authorization-header?", "nej → 401", MINT),
        ("verify_token()", "None → 401", MINT),
        ("get_user_roles()", "forkert rolle → 403", MINT),
        ("dit endpoint", "auth.current_user = user", DARK),
    ]
    for i, (step, outcome, fill) in enumerate(steps):
        x = 0.5 + i * 2.3
        dark = fill == DARK
        card(s, x, 1.5, 2.0, 1.2, fill)
        text(s, x + 0.1, 1.6, 1.8, 0.5, step, font=MONO, size=11, bold=True,
             color=WHITE if dark else DARK, align=PP_ALIGN.CENTER)
        text(s, x + 0.1, 2.15, 1.8, 0.45, outcome, size=12, color=PALE_TEXT if dark else BAD,
             align=PP_ALIGN.CENTER)
        if i < len(steps) - 1:
            shape(s, MSO_SHAPE.RIGHT_ARROW, x + 2.04, 1.98, 0.22, 0.24, CORAL)
    code_box(s, 0.5, 3.0, 9.0, 1.3,
             "@auth.verify_token\n"
             "def verify_token(token: str) -> dict | None:\n"
             "    user_id = read_token(token)\n"
             "    return None if user_id is None else get_user(user_id)", size=12)
    text(s, 0.5, 4.5, 9, 0.5, "Den dict, verify_token returnerer, er den samme som auth.current_user "
         "inde i endpointet.", size=13, italic=True, color=MUTED)


# --- Afsnit 3: roller ---------------------------------------------------------------


def slide_matrix():
    s = new_slide()
    title(s, "Role-based access control", "Rettigheder gives til roller. Personer får en rolle.")
    table(s, 0.5, 1.45, [3.0, 1.5, 1.5, 1.5, 1.5], [
        ["Endpoint", "admin", "doctor", "nurse", "uden token"],
        ["POST /login", "✓", "✓", "✓", "✓"],
        ["GET /me", "✓", "✓", "✓", "401"],
        ["GET /patients", "✓", "403", "✓", "401"],
        ["GET /my_patients", "403", "✓", "403", "401"],
        ["DELETE /patients/<id>", "✓", "403", "403", "401"],
    ], size=13, row_h=0.45, mono_cols=(0,))
    text(s, 0.5, 4.35, 9, 0.7,
         [[("Least privilege: ", {"bold": True, "color": DARK}),
           ("hver rolle får så få rettigheder som muligt. En læge behøver ikke se alle patienter.", {})]],
         size=14)


def slide_roles_code():
    s = new_slide()
    title(s, "Trin 6: roller i APIFlask", "Reglen står direkte på endpointet")
    code_box(s, 0.5, 1.45, 5.6, 1.5,
             "@app.get(\"/patients\")\n"
             "@app.auth_required(auth, roles=[\"admin\", \"nurse\"])\n"
             "def patients() -> list[dict]:\n"
             "    return all_patients()", size=11)
    code_box(s, 0.5, 3.1, 5.6, 1.1,
             "@auth.get_user_roles\n"
             "def get_user_roles(user: dict) -> str:\n"
             "    return user[\"role_name\"]", size=11)
    hint_cards(s, 6.35, 1.45, 3.15, [
        ("roles=[...]", "Brugeren skal have én af rollerne på listen."),
        ("Én gang", "get_user_roles fortæller APIFlask, hvor rollen står."),
        ("Tjek på serveren", "At skjule en knap beskytter intet. Alle kan sende en request."),
    ], card_h=0.9, gap=0.1, body_size=11)


def slide_row_level():
    s = new_slide()
    title(s, "Rolle er ikke nok: hvilke rækker?", "doctor må se patienter, men kun sine egne")
    columns = [
        (GOOD, "✓", "Id fra tokenet",
         "@app.get(\"/my_patients\")\n"
         "@app.auth_required(auth, roles=[\"doctor\"])\n"
         "def my_patients():\n"
         "    doctor_id = auth.current_user[\"doctor_id\"]\n"
         "    return patients_of_doctor(doctor_id)",
         "Brugeren kan ikke ændre, hvem den er."),
        (BAD, "✕", "Id fra URL'en",
         "@app.get(\"/patients_of_doctor/<int:doctor_id>\")\n"
         "@app.auth_required(auth, roles=[\"doctor\"])\n"
         "def patients_of(doctor_id):\n"
         "    return patients_of_doctor(doctor_id)",
         "Mette skriver /patients_of_doctor/2 og ser Jonas' patienter."),
    ]
    for i, (color, mark, heading, code, verdict) in enumerate(columns):
        x = 0.5 + i * 4.6
        badge(s, x, 1.45, mark, color)
        text(s, x + 0.6, 1.45, 3.8, 0.45, heading, font=HEAD, size=18, bold=True, color=color,
             anchor=MSO_ANCHOR.MIDDLE)
        code_box(s, x, 2.05, 4.4, 1.5, code, size=9)
        text(s, x, 3.7, 4.4, 0.6, verdict, size=13)
    text(s, 0.5, 4.5, 9, 0.5, "Det kaldes adgang på række-niveau. OWASP kalder fejlen \"Insecure Direct "
         "Object Reference\".", size=12, italic=True, color=MUTED)


def slide_dict_row():
    s = new_slide()
    title(s, "dict_row: rækker som dicts", "Et API sender JSON, og JSON har navne på felterne")
    code_box(s, 0.5, 1.45, 9.0, 1.1,
             "from psycopg.rows import dict_row\n"
             "\n"
             "with get_connection() as conn, conn.cursor(row_factory=dict_row) as cursor:", size=12)
    for i, (label, value, color) in enumerate([
        ("Uden dict_row", "(2, 'mette', 1, 'doctor')", MUTED),
        ("Med dict_row", "{'user_id': 2, 'username': 'mette',\n 'doctor_id': 1, 'role_name': 'doctor'}", TEAL),
    ]):
        x = 0.5 + i * 4.6
        text(s, x, 2.8, 4.4, 0.35, label, font=HEAD, size=15, bold=True, color=color)
        code_box(s, x, 3.2, 4.4, 0.9, value, size=11)
    text(s, 0.5, 4.35, 9, 0.6, "Flask laver en dict eller en liste af dicts om til JSON automatisk. "
         "user[\"role_name\"] er lettere at læse end user[3].", size=13, italic=True, color=MUTED)


def slide_checklist():
    s = new_slide()
    title(s, "Tjekliste: sikkerhed")
    table(s, 0.5, 1.2, [4.5, 4.5], [
        ["✓ Gør", "✕ Undgå"],
        ["Gem kun password_hash", "at gemme eller logge passwords"],
        ["Samme fejl for brugernavn og password", "\"Brugeren findes ikke\""],
        ["get_user() uden password_hash", "at sende hashet ud i et API-svar"],
        ["Tokens med exp", "tokens, der gælder for evigt"],
        ["\"Databasefejl\" til klienten, detaljer i loggen", "databasens fejlbesked til klienten"],
        ["HTTPS i produktion", "bearer tokens over almindelig HTTP"],
    ], size=12, row_h=0.47)


# --- Afsnit 4: sådan løser du trinene ------------------------------------------------


def slide_step4():
    s = new_slide()
    title(s, "Trin 4: check_login og POST /login", "flask --app app run --port 5001 --debug")
    code_box(s, 0.5, 1.45, 5.6, 1.35,
             "user = get_user_by_username(username)\n"
             "if user is None or not check_password_hash(\n"
             "        user[\"password_hash\"], password):\n"
             "    return None\n"
             "return user", size=11)
    code_box(s, 0.5, 2.95, 5.6, 1.35,
             "user = check_login(json_data[\"username\"],\n"
             "                   json_data[\"password\"])\n"
             "if user is None:\n"
             "    abort(401, \"Forkert brugernavn eller password\")\n"
             "return {\"token\": create_token(user[\"user_id\"])}", size=11)
    hint_cards(s, 6.35, 1.45, 3.15, [
        ("Port 5001", "Lektion 4-appen bruger 5000."),
        ("--debug", "Genstarter ved hver gemning. Nye tokens efter genstart!"),
        ("4.4 test i /docs", "Rigtigt login: 200. Forkert password og ukendt bruger: samme 401."),
    ], card_h=0.9, gap=0.1, body_size=11)


def slide_step5():
    s = new_slide()
    title(s, "Trin 5: get_user, verify_token og Authorize", "Og se, hvad der står i dit token")
    code_box(s, 0.5, 1.45, 5.6, 1.0,
             "user_id = read_token(token)\n"
             "if user_id is None:\n"
             "    return None\n"
             "return get_user(user_id)", size=11)
    code_box(s, 0.5, 2.6, 5.6, 1.45,
             ">>> import base64, json\n"
             ">>> header, payload, signature = token.split(\".\")\n"
             ">>> json.loads(base64.urlsafe_b64decode(payload + \"==\"))\n"
             "{'sub': '2', 'exp': 1791...}", size=10)
    hint_cards(s, 6.35, 1.45, 3.15, [
        ("5.1 get_user", "Som get_user_by_username, men uden password_hash og med WHERE user_id."),
        ("5.3 Authorize", "Indsæt kun tokenet. /docs skriver \"Bearer \" foran."),
        ("5.5 ret ét tegn", "Signaturen passer ikke → 401."),
    ], card_h=0.9, gap=0.1, body_size=11)
    text(s, 0.5, 4.25, 9, 0.7,
         [[("✅ Tjek: ", {"bold": True, "color": GOOD}),
           ("GET /me med token → {\"username\": \"mette\", \"role\": \"doctor\"}. Uden token → 401.", {})]],
         size=14)


def slide_step6():
    s = new_slide()
    title(s, "Trin 6: roller og egne patienter", "6.1 get_user_roles · 6.3 patients_of_doctor · 6.4 roles=[...]")
    code_box(s, 0.5, 1.45, 5.6, 1.8,
             "query = t\"\"\"\n"
             "    SELECT patient_id, first_name, last_name,\n"
             "           age, blood_type, allergies\n"
             "    FROM patient\n"
             "    WHERE doctor_id = {doctor_id}\n"
             "    ORDER BY patient_id\n"
             "\"\"\"", size=11)
    table(s, 0.5, 3.45, [2.6, 3.0], [
        ["Endpoint", "roles="],
        ["/patients", "[\"admin\", \"nurse\"]"],
        ["/my_patients", "[\"doctor\"]"],
        ["DELETE /patients/<id>", "[\"admin\"]"],
    ], size=11, row_h=0.33, mono_cols=(0, 1))
    hint_cards(s, 6.35, 1.45, 3.15, [
        ("dict_row", "Samme with-linje som i all_patients."),
        ("6.5 test som nina", "/patients → 200, /my_patients → 403"),
        ("6.5 test som mette", "/my_patients → Kevin, Karen, Erik"),
    ], card_h=0.9, gap=0.1, body_size=11)


def slide_step7():
    s = new_slide()
    title(s, "Trin 7: test alle regler med client.py", "Lad app'en køre, og kør uv run client.py i en anden terminal")
    code_box(s, 0.5, 1.45, 4.3, 1.8,
             "credentials = {\"username\": username,\n"
             "               \"password\": password}\n"
             "response = requests.post(\n"
             "    f\"{API_URL}/login\",\n"
             "    json=credentials, timeout=5)\n"
             "response.raise_for_status()\n"
             "return response.json()[\"token\"]", size=10)
    code_box(s, 0.5, 3.4, 4.3, 0.75,
             "headers = ({\"Authorization\": f\"Bearer {token}\"}\n"
             "           if token else {})", size=10)
    code_box(s, 5.0, 1.45, 4.5, 2.1,
             "                admin mette  nina uden\n"
             "GET /me          200   200   200  401\n"
             "GET /patients    200   403   200  401\n"
             "GET /my_patients 403   200   403  401\n"
             "DELETE …/999     404   403   403  401\n"
             "Forkert password giver: 401", size=10)
    text(s, 5.0, 3.7, 4.5, 1.2,
         "Tabellen er en test: ændrer nogen en roles=[...] ved en fejl, ændrer tabellen sig. "
         "I del 4 automatiserer vi det med pytest.", size=13, italic=True, color=TEAL)


def slide_errors():
    s = new_slide()
    title(s, "Almindelige fejl og hvad de betyder")
    table(s, 0.5, 1.2, [4.6, 4.4], [
        ["Du ser", "Det betyder"],
        ["No module named 'apiflask'", "kør uv sync i sundhedsapp_postgres"],
        ["Address already in use / port 5000", "husk --port 5001"],
        ["401 efter du gemte en fil", "--debug genstartede serveren: log ind igen"],
        ["500 + NotImplementedError: trin …", "godt! Skriv det trin, der står i terminalen"],
        ["NotNullViolation: role_id", "rollenavnet findes ikke i role (stavefejl?)"],
        ["relation \"role\" does not exist", "kør schema.sql (trin 2) igen"],
        ["ConnectionError i client.py", "app'en kører ikke på port 5001"],
    ], size=11, row_h=0.45, mono_cols=(0,))


# --- Afslutning ------------------------------------------------------------------------


def slide_links():
    s = new_slide()
    title(s, "Læs mere", "Alle links står også nederst i theory.md")
    groups = [
        ("Login og tokens", [
            ("APIFlask: authentication", "https://apiflask.com/authentication/"),
            ("Flask-HTTPAuth: roles",
             "https://flask-httpauth.readthedocs.io/en/latest/#user-roles"),
            ("joserfc: JWT", "https://jose.authlib.org/en/guide/jwt/"),
            ("RFC 7519: JWT", "https://datatracker.ietf.org/doc/html/rfc7519"),
        ]),
        ("Sikkerhed", [
            ("Werkzeug: password hash",
             "https://werkzeug.palletsprojects.com/en/stable/utils/#module-werkzeug.security"),
            ("OWASP: password storage",
             "https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html"),
            ("OWASP: authentication",
             "https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html"),
            ("OWASP: authorization",
             "https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html"),
        ]),
        ("PostgreSQL og psycopg", [
            ("SQL key words (USER)",
             "https://www.postgresql.org/docs/current/sql-keywords-appendix.html"),
            ("UNIQUE constraints",
             "https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-UNIQUE-CONSTRAINTS"),
            ("psycopg: row factories", "https://www.psycopg.org/psycopg3/docs/advanced/rows.html"),
            ("MDN: 401", "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/401"),
            ("MDN: 403", "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/403"),
        ]),
    ]
    for i, (heading, links) in enumerate(groups):
        x = 0.5 + i * 3.05
        card(s, x, 1.45, 2.85, 3.0)
        text(s, x + 0.2, 1.6, 2.5, 0.35, heading, font=HEAD, size=16, bold=True, color=DARK)
        lines_ = [[(label, {"color": TEAL, "link": url})] for label, url in links]
        text(s, x + 0.2, 2.05, 2.5, 3.0, lines_, size=13, space_after=7)


def slide_roadmap():
    roadmap('Din tur: exercise.md, trin 4–7', [
        ('4', 'Login', 'check_login + /login', 9),
        ('5', 'Token', 'verify_token + /me', 7),
        ('6', 'Roller', 'roles=[...]', 8),
        ('7', 'Test', 'client.py', 6),
    ], [
        [('Hav to terminaler åbne: ', {"bold": True, "color": DARK}),
         ('én med flask run --port 5001 --debug, og én til uv run og '
          'client.py.', {})],
        [('Sidder du fast? ', {"bold": True, "color": DARK}),
         ('1) læs fejlen i flask-terminalen  2) læs TODO-hintet  3) '
          'find slidet for trinnet  4) kig i solution/', {})],
        [('Færdig før tid? ', {"bold": True, "color": DARK}),
         ('Ekstraopgaver: udløb, POST /patients, skift password, flere '
          'roller, GRANT.', {})],
    ])


def main() -> None:
    use_part(3)
    slide_title()
    slide_plan()
    slide_problem()
    section(1, "Brugere og roller i databasen", "ER diagram → CREATE TABLE → hashede passwords (trin 1–3)")
    slide_erd()
    slide_app_user_sql()
    slide_hashing()
    slide_salt()
    section(2, "Login og tokens", "POST /login, JWT og verify_token (trin 4–5)")
    slide_flow()
    slide_jwt()
    slide_joserfc()
    slide_auth_required()
    section(3, "Role-based access control", "Roller, rækker og sikkerhed (trin 6–7)")
    slide_matrix()
    slide_roles_code()
    slide_row_level()
    slide_dict_row()
    slide_checklist()
    section(4, "Sådan løser du trin 4–7", "Mønstre, hints og de tjek, du skal kigge efter")
    slide_step4()
    slide_step5()
    slide_step6()
    slide_step7()
    slide_errors()
    slide_links()
    slide_roadmap()
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else OUT
    try:
        save(out, "Del 3 - Login og role-based access control")
    except PermissionError:
        sys.exit(f"Kan ikke skrive {out}. Luk den i PowerPoint, og kør igen.")
    print(f"skrev {out}")


if __name__ == "__main__":
    main()
