"""Byg del2_theory.pptx til del 2: hospitaler, JOIN, GROUP BY, HAVING og stored procedures.

Bygget på EK-skabelonen via kit.py. Del 2 bruger sin egen farvefamilie (use_part(2)).

Kør fra mappen sundhedsapp_postgres (luk præsentationen i PowerPoint først):

    uv run --with python-pptx slides/build_del2.py

Et valgfrit argument gemmer præsentationen et andet sted: build_del2.py other.pptx
"""

import sys
from pathlib import Path

from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN

from kit import (
    BAD, CORAL, DARK, GOOD, HEAD, INK, MINT, MONO, MUTED, PALE_TEXT, TEAL, WARN_BG, WHITE,
    arrow, badge, card, code_box, entity, hint_cards, new_slide, notes, one_to_many,
    roadmap, save, section, shape, table, text, title, title_slide, use_part, warning,
)


OUT = Path(__file__).parent.parent / "del2_hospital" / "del2_theory.pptx"

GROUP_COLORS = [MINT, WARN_BG, "E6ECF8", "FFF3D1"]


# --- Intro -----------------------------------------------------------------------


def slide_title():
    title_slide('Lektion 5 · Del 2', 'Hospitaler, læger og patienter',
                'Fra én tabel til tre: relationships, JOIN, GROUP BY og stored procedures',
                ['Foreign keys', 'JOIN', 'GROUP BY + HAVING', 'Stored procedures'],
                'Opsummering af del 1: én patient-tabel med constraints, CRUD med t-strings og executemany(). I dag får patienterne en læge, og lægerne et hospital.')


def slide_plan():
    s = new_slide()
    title(s, "Planen for del 2", "Trin 1–3 hjemme, trin 4–7 i undervisningen")
    columns = [
        ("Hjemme", TEAL, [
            ("P", "Læs theory.md, ret password i db.py"),
            ("1", "Udvid ER diagrammet"),
            ("2", "CREATE TABLE med foreign keys"),
            ("3", "Fyld tabellerne (seed.py)"),
        ]),
        ("I undervisningen", CORAL, [
            ("4", "JOIN: sæt tabellerne sammen"),
            ("5", "GROUP BY: tæl og regn per gruppe"),
            ("6", "HAVING: filtrér grupper"),
            ("7", "Stored procedures"),
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
    title(s, "Hvorfor ikke bare flere kolonner i patient?",
          "Én stor tabel gentager de samme oplysninger igen og igen")
    table(s, 0.5, 1.5, [1.1, 1.3, 2.0, 1.9, 1.2], [
        ["patient_id", "first_name", "doctor_name", "hospital_name", "bed_count"],
        ["1", "Kevin", "Mette Sørensen", "Rigshospitalet", "1100"],
        ["2", "Karen", "Mette Sørensen", "Rigshospitalet", "1100"],
        ["3", "Erik", "Mette Sørensen", "Rigshospitalet", "1100"],
    ], size=12, row_h=0.4, mono_cols=(0, 1, 2, 3, 4), first_fill=BAD)
    hint_cards(s, 0.5, 3.35, 4.4, [
        ("Redundans", "Rigshospitalet får flere senge: du skal ændre alle rækker. Glemmer du én, "
                      "er data uenige med sig selv."),
    ], card_h=1.2)
    card(s, 5.1, 3.35, 4.4, 1.2, DARK)
    text(s, 5.3, 3.45, 4.0, 0.35, "Løsningen: én tabel per ting", font=HEAD, size=14, bold=True,
         color=WHITE)
    text(s, 5.3, 3.85, 4.0, 0.6, "hospital  1 ──< doctor  1 ──< patient", font=MONO, size=13,
         color=PALE_TEXT, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 0.5, 4.75, 9, 0.4, "ER-metoden trin 7 fra del 1: \"Beskriver hver kolonne denne entity?\"",
         size=13, italic=True, color=MUTED)


# --- Afsnit 1: relationships ------------------------------------------------------


def slide_erd():
    s = new_slide()
    title(s, "ER diagrammet for del 2", "To one-to-many relationships. FK = foreign key.")
    entity(s, 0.5, 1.4, 2.4, "hospital", [
        ("PK", "hospital_id", "integer"),
        ("", "hospital_name", "text"),
        ("", "bed_count", "integer"),
    ])
    entity(s, 3.8, 1.4, 2.4, "doctor", [
        ("PK", "doctor_id", "integer"),
        ("", "doctor_name", "text"),
        ("FK", "hospital_id", "integer"),
        ("", "joining_date", "date"),
        ("", "speciality", "text"),
        ("", "salary", "integer"),
        ("", "experience", "int·null"),
    ])
    entity(s, 7.1, 1.4, 2.4, "patient", [
        ("PK", "patient_id", "integer"),
        ("", "first_name", "text"),
        ("", "last_name", "text"),
        ("", "age", "integer"),
        ("", "blood_type", "text"),
        ("", "allergies", "text·null"),
        ("FK", "doctor_id", "integer"),
    ])
    one_to_many(s, 2.9, 3.8, 1.62)
    one_to_many(s, 6.2, 7.1, 1.62)
    text(s, 0.5, 3.05, 2.4, 1.6,
         "Ét hospital har nul eller flere læger.\n\nÉn læge har nul eller flere patienter.",
         size=12, italic=True, color=MUTED)
    notes(s, "Bornholms Hospital har ingen læger, og Oliver Poulsen har ingen patienter. "
             "Derfor 'nul eller flere' (o<) og ikke 'én eller flere' (|<).")


def slide_fk_side():
    s = new_slide()
    title(s, "Hvor skal foreign key'en stå?", "Sig relationship'et i begge retninger, og find \"mange\"")
    pairs = [
        ("Et hospital har mange læger.", "En læge arbejder på ét hospital.", "doctor.hospital_id"),
        ("En læge har mange patienter.", "En patient har én læge.", "patient.doctor_id"),
    ]
    for i, (many, one, fk) in enumerate(pairs):
        y = 1.5 + i * 1.3
        card(s, 0.5, y, 5.6, 1.1)
        text(s, 0.7, y + 0.12, 5.2, 0.9,
             [[(many, {})], [(one, {})]], size=15, space_after=6)
        arrow(s, 6.25, y + 0.41)
        card(s, 6.7, y, 2.8, 1.1, DARK)
        text(s, 6.7, y, 2.8, 1.1, fk, font=MONO, size=14, bold=True, color=WHITE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 0.5, 4.2, 9, 0.9,
         [[("Reglen: ", {"bold": True, "color": CORAL}),
           ("i et one-to-many relationship står foreign key'en altid på mange-siden. "
            "Et hospital kan ikke have en doctor_id: der er ikke plads til mange læger i én celle.", {})]],
         size=15)


def slide_given_sql():
    s = new_slide()
    title(s, "Trin 1.5: den udleverede SQL", "Den virker, men har fire svagheder")
    code_box(s, 0.5, 1.45, 4.3, 2.85,
             "CREATE TABLE Doctor (\n"
             "  Doctor_Id INTEGER NOT NULL\n"
             "            PRIMARY KEY,\n"
             "  Doctor_Name TEXT NOT NULL,\n"
             "  Hospital_Id INTEGER NOT NULL,\n"
             "  Joining_Date TEXT NOT NULL,\n"
             "  Speciality TEXT NOT NULL,\n"
             "  Salary INTEGER NOT NULL,\n"
             "  Experience INTEGER\n"
             ");", size=11)
    fixes = [
        ("1", "Hospital_Id er bare et tal", "→ REFERENCES hospital (hospital_id)"),
        ("2", "Joining_Date TEXT tager 'i går'", "→ DATE"),
        ("3", "Vi skal selv finde på id'er", "→ GENERATED ALWAYS AS IDENTITY"),
        ("4", "Store_Og_Små bliver små alligevel", "→ snake_case: hospital_id"),
    ]
    for i, (number, problem, fix) in enumerate(fixes):
        y = 1.45 + i * 0.73
        card(s, 5.05, y, 4.45, 0.63)
        badge(s, 5.15, y + 0.1, number, CORAL, size=0.42)
        text(s, 5.7, y + 0.05, 3.7, 0.28, problem, size=12, bold=True, color=DARK)
        text(s, 5.7, y + 0.32, 3.7, 0.28, fix, font=MONO, size=10, color=TEAL)
    text(s, 0.5, 4.5, 9, 0.6,
         "PostgreSQL laver navne uden \"anførselstegn\" om til små bogstaver: Hospital_Id er hospital_id.",
         size=13, italic=True, color=MUTED)


def slide_references():
    s = new_slide()
    title(s, "Trin 2: REFERENCES i praksis", "Databasen håndhæver relationship'et begge veje")
    code_box(s, 0.5, 1.45, 9.0, 0.75,
             "hospital_id  INTEGER NOT NULL REFERENCES hospital (hospital_id),", size=13)
    cases = [
        ("Indsæt en læge på hospital 99",
         "INSERT INTO doctor (..., hospital_id, ...)\nVALUES (..., 99, ...);",
         "Key (hospital_id)=(99) is not present\nin table \"hospital\""),
        ("Slet et hospital med læger",
         "DELETE FROM hospital\nWHERE hospital_id = 1;",
         "Key (hospital_id)=(1) is still\nreferenced from table \"doctor\""),
    ]
    for i, (heading, sql, error) in enumerate(cases):
        x = 0.5 + i * 4.6
        text(s, x, 2.4, 4.4, 0.35, heading, font=HEAD, size=15, bold=True, color=DARK)
        code_box(s, x, 2.8, 4.4, 0.8, sql, size=11)
        card(s, x, 3.7, 4.4, 0.8, WARN_BG)
        text(s, x + 0.15, 3.75, 4.1, 0.7, error, font=MONO, size=10, color=BAD,
             anchor=MSO_ANCHOR.MIDDLE)
    text(s, 0.5, 4.7, 9, 0.4, "Det kaldes referentiel integritet: ingen læge peger på et hospital, "
         "der ikke findes.", size=13, italic=True, color=MUTED)


def slide_order():
    s = new_slide()
    title(s, "Rækkefølgen betyder noget", "Man kan kun pege på noget, der findes")
    table(s, 0.5, 1.45, [2.3, 3.6, 3.1], [
        ["Handling", "Rækkefølge", "Hvorfor"],
        ["CREATE TABLE", "hospital → doctor → patient", "REFERENCES kræver tabellen"],
        ["INSERT", "hospital → doctor → patient", "FK'en skal findes"],
        ["DELETE / DROP", "patient → doctor → hospital", "ingen må pege på den"],
    ], size=13, row_h=0.48, mono_cols=(0, 1))
    text(s, 0.5, 3.6, 9, 0.35, "Genvejen: nævn alle tabellerne i ét statement", font=HEAD,
         size=15, bold=True, color=DARK)
    code_box(s, 0.5, 4.0, 9.0, 0.85,
             "DROP TABLE IF EXISTS patient, doctor, hospital;\n"
             "TRUNCATE patient, doctor, hospital RESTART IDENTITY;   -- tøm, og start id'er ved 1",
             size=12)


def slide_pgadmin():
    s = new_slide()
    title(s, "Trin 1.6: One-to-Many i pgAdmin 9.18", "ERD Tool: tegn relationship'et, og lad pgAdmin skrive FK'en")
    steps = [
        "Højreklik på sundhedsapp → ERD For Database",
        "Add table: hospital og doctor",
        "joining_date = date, id'er = IDENTITY / ALWAYS",
        "Tilføj doctor_id (integer) i patient",
        "Marker doctor (mange-siden)",
        "Klik One-to-Many i værktøjslinjen",
        "Local column hospital_id → hospital.hospital_id",
        "Gentag for patient.doctor_id, gem som hospital.pgerd",
    ]
    for i, step in enumerate(steps):
        x = 0.5 + (i // 4) * 4.6
        y = 1.5 + (i % 4) * 0.72
        badge(s, x, y, str(i + 1), TEAL, size=0.45)
        text(s, x + 0.6, y, 3.8, 0.45, step, size=14, anchor=MSO_ANCHOR.MIDDLE)
    warning(s, 4.55, "Tip: ", "Generate SQL viser FK'en som ALTER TABLE ... ADD FOREIGN KEY. "
                             "Det er det samme som REFERENCES.")


# --- Afsnit 2: JOIN, GROUP BY, HAVING ---------------------------------------------


def slide_join():
    s = new_slide()
    title(s, "JOIN: sæt tabellerne sammen igen", "ON siger, hvilke rækker der hører sammen: FK = PK")
    code_box(s, 0.5, 1.45, 5.4, 1.35,
             "SELECT d.doctor_name, h.hospital_name\n"
             "FROM doctor AS d\n"
             "JOIN hospital AS h\n"
             "  ON h.hospital_id = d.hospital_id;", size=12)
    hint_cards(s, 6.15, 1.45, 3.35, [
        ("AS d, AS h", "Aliaser: korte navne. Påkrævet, når to tabeller har samme kolonnenavn."),
        ("ON", "Foreign key = primary key. Uden ON hører alle rækker sammen."),
    ], card_h=1.0, gap=0.15, body_size=12)
    text(s, 0.5, 3.0, 5.4, 0.35, "Resultat (uddrag):", font=HEAD, size=13, bold=True, color=DARK)
    table(s, 0.5, 3.35, [2.6, 2.8], [
        ["doctor_name", "hospital_name"],
        ["Mette Sørensen", "Rigshospitalet"],
        ["Ali Hassan", "Aarhus Universitetshospital"],
    ], size=11, row_h=0.34, mono_cols=(0, 1))
    warning(s, 4.6, "Uden ON: ", "FROM doctor, hospital giver 9 × 5 = 45 rækker (kartesisk produkt).",
            h=0.55)


def slide_left_join():
    s = new_slide()
    title(s, "JOIN eller LEFT JOIN?", "Hvad sker der med et hospital uden læger?")
    columns = [
        ("JOIN", "kun rækker med et match", [
            ["hospital_name", "doctor_name"],
            ["Rigshospitalet", "Mette Sørensen"],
            ["Aalborg Univ.", "Ida Rasmussen"],
        ], "Bornholm forsvinder."),
        ("LEFT JOIN", "alle rækker fra venstre tabel", [
            ["hospital_name", "doctor_name"],
            ["Rigshospitalet", "Mette Sørensen"],
            ["Aalborg Univ.", "Ida Rasmussen"],
            ["Bornholms Hospital", "NULL"],
        ], "Bornholm er med, med NULL."),
    ]
    for i, (name, meaning, rows, verdict) in enumerate(columns):
        x = 0.5 + i * 4.6
        text(s, x, 1.45, 4.4, 0.4, name, font=MONO, size=18, bold=True, color=TEAL if i else DARK)
        text(s, x, 1.85, 4.4, 0.3, meaning, size=13, italic=True, color=MUTED)
        table(s, x, 2.3, [2.2, 2.2], rows, size=11, row_h=0.36, mono_cols=(0, 1))
        text(s, x, 3.85, 4.4, 0.35, verdict, size=14, bold=True, color=BAD if i == 0 else GOOD)
    code_box(s, 0.5, 4.4, 9.0, 0.6,
             "FROM hospital AS h LEFT JOIN doctor AS d ON d.hospital_id = h.hospital_id", size=12)


def slide_aggregates():
    s = new_slide()
    title(s, "Aggregatfunktioner: mange rækker → én værdi")
    table(s, 0.5, 1.2, [2.2, 2.9, 1.6], [
        ["Funktion", "Giver", "doctor"],
        ["COUNT(*)", "antal rækker", "9"],
        ["COUNT(experience)", "antal, der ikke er NULL", "7"],
        ["SUM(salary)", "summen", "564000"],
        ["AVG(salary)", "gennemsnittet", "62666.67…"],
        ["MIN / MAX(salary)", "mindste / største", "50000 / 78000"],
    ], size=12, row_h=0.42, mono_cols=(0, 2))
    hint_cards(s, 7.4, 1.2, 2.1, [
        ("NULL", "springes over. To læger har ukendt experience."),
        ("::integer", "caster AVG til et heltal og runder."),
    ], card_h=1.25, gap=0.15, body_size=12)
    text(s, 0.5, 4.0, 9, 0.9,
         [[("Uden GROUP BY ", {"bold": True, "color": DARK}),
           ("regner en aggregatfunktion på hele tabellen og giver én række. ", {}),
           ("Med GROUP BY ", {"bold": True, "color": TEAL}),
           ("regner den én gang per gruppe.", {})]], size=15)


def slide_group_by():
    s = new_slide()
    title(s, "GROUP BY: læg rækkerne i bunker", "SELECT speciality, COUNT(*), AVG(salary)::integer FROM doctor GROUP BY speciality")
    doctors = [
        (0, "Almen medicin", "Oliver Poulsen", "50000"),
        (0, "Almen medicin", "Ida Rasmussen", "60000"),
        (1, "Kardiologi", "Mette Sørensen", "72000"),
        (1, "Kardiologi", "Jonas Madsen", "58000"),
        (1, "Kardiologi", "Peter Larsen", "69000"),
        (2, "Ortopædkirurgi", "Ali Hassan", "78000"),
        (2, "Ortopædkirurgi", "Freja Andersen", "64000"),
        (3, "Pædiatri", "Sara Nielsen", "61000"),
        (3, "Pædiatri", "Emma Kristensen", "52000"),
    ]
    for i, (group, speciality, name, salary) in enumerate(doctors):
        y = 1.45 + i * 0.37 + group * 0.06
        shape(s, MSO_SHAPE.RECTANGLE, 0.5, y, 4.6, 0.33, GROUP_COLORS[group])
        text(s, 0.6, y, 1.7, 0.33, speciality, size=11, bold=True, anchor=MSO_ANCHOR.MIDDLE)
        text(s, 2.3, y, 1.8, 0.33, name, size=11, anchor=MSO_ANCHOR.MIDDLE)
        text(s, 4.1, y, 0.9, 0.33, salary, font=MONO, size=11, anchor=MSO_ANCHOR.MIDDLE)
    arrow(s, 5.3, 2.95)
    results = [
        ("Almen medicin", "2", "55000"),
        ("Kardiologi", "3", "66333"),
        ("Ortopædkirurgi", "2", "71000"),
        ("Pædiatri", "2", "56500"),
    ]
    text(s, 5.8, 1.45, 3.7, 0.3, "speciality · count · avg", font=MONO, size=11, bold=True, color=DARK)
    for i, (speciality, count, avg) in enumerate(results):
        y = 1.95 + i * 0.6
        shape(s, MSO_SHAPE.RECTANGLE, 5.8, y, 3.7, 0.48, GROUP_COLORS[i])
        text(s, 5.9, y, 1.9, 0.48, speciality, size=12, bold=True, anchor=MSO_ANCHOR.MIDDLE)
        text(s, 7.8, y, 0.5, 0.48, count, font=MONO, size=12, anchor=MSO_ANCHOR.MIDDLE)
        text(s, 8.4, y, 1.0, 0.48, avg, font=MONO, size=12, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 5.8, 4.45, 3.7, 0.6, "9 rækker ind, 4 grupper ud. Én række per bunke.", size=13,
         italic=True, color=TEAL)


def slide_group_rule():
    s = new_slide()
    title(s, "Reglen for GROUP BY", "Hver kolonne i SELECT står i GROUP BY eller i en aggregatfunktion")
    code_box(s, 0.5, 1.45, 9.0, 0.6,
             "SELECT speciality, doctor_name, COUNT(*) FROM doctor GROUP BY speciality;", size=12)
    card(s, 0.5, 2.2, 9.0, 0.75, WARN_BG)
    text(s, 0.7, 2.2, 8.6, 0.75,
         "ERROR: column \"doctor.doctor_name\" must appear in the GROUP BY clause\n"
         "       or be used in an aggregate function", font=MONO, size=11, color=BAD,
         anchor=MSO_ANCHOR.MIDDLE)
    hint_cards(s, 0.5, 3.15, 4.4, [
        ("Hvorfor?", "Bunken Kardiologi har tre læger. Hvilket navn skulle PostgreSQL vise? "
                     "Det kan den ikke vide."),
    ], card_h=1.25)
    hint_cards(s, 5.1, 3.15, 4.4, [
        ("Med JOIN", "GROUP BY h.hospital_name og COUNT(d.doctor_id). "
                     "COUNT(*) ville tælle Bornholms NULL-række som 1."),
    ], card_h=1.25)


def slide_having():
    s = new_slide()
    title(s, "HAVING: filtrér grupper", "WHERE smider rækker væk. HAVING smider bunker væk.")
    steps = [
        ("FROM / JOIN", False), ("WHERE", True), ("GROUP BY", False), ("HAVING", True),
        ("SELECT", False), ("ORDER BY", False),
    ]
    for i, (step, highlight) in enumerate(steps):
        x = 0.5 + i * 1.55
        card(s, x, 1.45, 1.3, 0.6, CORAL if highlight else MINT)
        text(s, x, 1.45, 1.3, 0.6, step, font=MONO, size=12, bold=True,
             color=WHITE if highlight else DARK, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        text(s, x, 2.1, 1.3, 0.3, str(i + 1), size=11, color=MUTED, align=PP_ALIGN.CENTER)
        if i < len(steps) - 1:
            shape(s, MSO_SHAPE.RIGHT_ARROW, x + 1.32, 1.66, 0.2, 0.2, TEAL)
    text(s, 0.5, 2.45, 9, 0.35, "Den rækkefølge PostgreSQL udfører en query i. Ved WHERE findes der "
         "endnu ingen grupper at tælle.", size=12, italic=True, color=MUTED)
    code_box(s, 0.5, 2.95, 5.4, 1.65,
             "SELECT speciality, AVG(salary)::integer\n"
             "FROM doctor\n"
             "WHERE hospital_id = 1         -- rækker\n"
             "GROUP BY speciality\n"
             "HAVING AVG(salary) > 60000;   -- grupper", size=11)
    hint_cards(s, 6.15, 2.95, 3.35, [
        ("WHERE COUNT(*) >= 3", "ERROR: aggregate functions are not allowed in WHERE"),
        ("Tommelfingerregel", "Én række nok? WHERE. Skal der tælles først? HAVING."),
    ], card_h=0.8, gap=0.07, body_size=11)


# --- Afsnit 3: stored procedures ---------------------------------------------------


def slide_function_vs_procedure():
    s = new_slide()
    title(s, "Stored procedures: kode, der bor i databasen", "I PostgreSQL findes to slags")
    kinds = [
        ("FUNCTION", "returnerer data", "SELECT * FROM\n  doctors_by_speciality('Kardiologi');", TEAL),
        ("PROCEDURE", "udfører en handling", "CALL raise_salary('Pædiatri', 10);", CORAL),
    ]
    for i, (name, purpose, call, color) in enumerate(kinds):
        x = 0.5 + i * 4.6
        card(s, x, 1.45, 4.4, 2.6)
        text(s, x + 0.2, 1.6, 4.0, 0.45, name, font=MONO, size=22, bold=True, color=color)
        text(s, x + 0.2, 2.1, 4.0, 0.35, purpose, size=15, italic=True, color=MUTED)
        text(s, x + 0.2, 2.55, 4.0, 0.3, "Kaldes med:", size=13, bold=True, color=DARK)
        code_box(s, x + 0.2, 2.9, 4.0, 0.95, call, size=11)
    text(s, 0.5, 4.3, 9, 0.7, "I daglig tale kalder man begge for stored procedures. "
         "CREATE OR REPLACE betyder, at du kan køre filen igen efter en ændring.",
         size=14, color=INK)


def slide_function_anatomy():
    s = new_slide()
    title(s, "Trin 7.1: anatomien af en function", "Kroppen mellem $$ og $$ er en almindelig SELECT")
    code_box(s, 0.5, 1.45, 5.6, 3.3,
             "CREATE OR REPLACE FUNCTION\n"
             "  doctors_by_speciality(p_speciality TEXT)\n"
             "RETURNS TABLE (doctor_name TEXT,\n"
             "               hospital_name TEXT,\n"
             "               salary INTEGER)\n"
             "LANGUAGE sql\n"
             "AS $$\n"
             "  SELECT d.doctor_name, h.hospital_name, d.salary\n"
             "  FROM doctor AS d JOIN hospital AS h ...\n"
             "  WHERE d.speciality = p_speciality;\n"
             "$$;", size=11)
    parts = [
        ("p_speciality TEXT", "parameteren. p_ = ikke en kolonne."),
        ("RETURNS TABLE (…)", "kolonnerne i resultatet"),
        ("LANGUAGE sql", "kroppen er ren SQL"),
        ("$$ … $$", "anførselstegn om kroppen"),
    ]
    for i, (heading, body) in enumerate(parts):
        y = 1.45 + i * 0.84
        card(s, 6.35, y, 3.15, 0.74)
        text(s, 6.5, y + 0.07, 2.9, 0.3, heading, font=MONO, size=12, bold=True, color=CORAL)
        text(s, 6.5, y + 0.38, 2.9, 0.3, body, size=12)


def slide_procedure():
    s = new_slide()
    title(s, "Trin 7.3: en procedure med PL/pgSQL", "Når koden skal træffe beslutninger eller melde fejl")
    code_box(s, 0.5, 1.45, 5.6, 3.35,
             "CREATE OR REPLACE PROCEDURE\n"
             "  raise_salary(p_speciality TEXT, p_percent INTEGER)\n"
             "LANGUAGE plpgsql\n"
             "AS $$\n"
             "BEGIN\n"
             "  UPDATE doctor\n"
             "  SET salary = salary + salary * p_percent / 100\n"
             "  WHERE speciality = p_speciality;\n"
             "\n"
             "  IF NOT FOUND THEN\n"
             "    RAISE EXCEPTION 'Ingen læger med specialet %',\n"
             "                    p_speciality;\n"
             "  END IF;\n"
             "END;\n"
             "$$;", size=10)
    hint_cards(s, 6.35, 1.45, 3.15, [
        ("BEGIN … END;", "Omslutter koden. Hvert statement slutter med ;"),
        ("FOUND", "true, hvis sidste statement ramte mindst én række."),
        ("RAISE EXCEPTION", "Stopper, ruller UPDATE tilbage og sender fejlen. % = værdien."),
    ], card_h=1.02, gap=0.14, body_size=11)


def slide_call_from_python():
    s = new_slide()
    title(s, "Trin 7.4–7.6: kald dem fra Python", "Præcis som alle andre queries, med t-strings")
    code_box(s, 0.5, 1.45, 9.0, 1.05,
             "conn.execute(t\"SELECT * FROM doctors_by_speciality({speciality})\").fetchall()\n"
             "\n"
             "conn.execute(t\"CALL raise_salary({speciality}, {percent})\")     # ingen fetch", size=12)
    code_box(s, 0.5, 2.7, 5.6, 1.5,
             "from psycopg.errors import RaiseException\n"
             "\n"
             "try:\n"
             "    raise_salary(\"Tandlæge\", 10)\n"
             "except RaiseException as error:\n"
             "    logger.warning(\"Afvist: %s\", error.diag.message_primary)", size=10)
    hint_cards(s, 6.35, 2.7, 3.15, [
        ("RAISE EXCEPTION", "bliver til RaiseException i Python."),
        ("Nulstil", "Hver kørsel hæver lønnen. Kør seed.py igen."),
    ], card_h=0.8, gap=0.06, body_size=11)
    code_box(s, 0.5, 4.45, 9.0, 0.5,
             "Afvist af proceduren: Ingen læger med specialet Tandlæge", size=11)


def slide_pros_cons():
    s = new_slide()
    title(s, "Hvornår giver det mening?", "Stored procedures er et værktøj, ikke et mål")
    columns = [
        (GOOD, "✓", "Fordele", [
            "Reglen virker for alle programmer, der bruger databasen",
            "Kun én tur til databasen, selv for mange statements",
            "Kan ikke omgås af kode, der \"glemmer\" reglen",
        ]),
        (BAD, "✕", "Ulemper", [
            "Logikken er delt mellem Python og SQL",
            "Sværere at teste og versionsstyre",
            "PL/pgSQL er endnu et sprog at lære",
        ]),
    ]
    for i, (color, mark, heading, points) in enumerate(columns):
        x = 0.5 + i * 4.6
        badge(s, x, 1.45, mark, color)
        text(s, x + 0.6, 1.45, 3.8, 0.45, heading, font=HEAD, size=19, bold=True, color=color,
             anchor=MSO_ANCHOR.MIDDLE)
        text(s, x, 2.1, 4.4, 1.8, "\n".join(f"• {point}" for point in points), size=14,
             space_after=8)
    text(s, 0.5, 4.2, 9, 0.8,
         [[("Tommelfingerregel: ", {"bold": True, "color": DARK}),
           ("regler om data hører hjemme i databasen. Regler om brugeren (login, visning) "
            "hører hjemme i Python. Det er emnet for del 3.", {})]], size=14)


# --- Afsnit 4: sådan løser du trinene ----------------------------------------------


def slide_step3():
    s = new_slide()
    title(s, "Trin 3: fyld tabellerne", "Samme executemany() som i del 1, nu med seks kolonner")
    code_box(s, 0.5, 1.45, 5.6, 1.7,
             "sql = \"\"\"\n"
             "  INSERT INTO doctor (doctor_name, hospital_id,\n"
             "      joining_date, speciality, salary, experience)\n"
             "  VALUES (%s, %s, %s, %s, %s, %s)\n"
             "\"\"\"\n"
             "cursor.executemany(sql, DOCTORS)\n"
             "return cursor.rowcount", size=10)
    code_box(s, 0.5, 3.3, 5.6, 1.3,
             "with get_connection() as conn, conn.cursor() as cursor:\n"
             "    cursor.execute(\"TRUNCATE ... RESTART IDENTITY\")\n"
             "    insert_hospitals(cursor)   # 1\n"
             "    insert_doctors(cursor)     # 2\n"
             "    insert_patients(cursor, rows)  # 3", size=10)
    hint_cards(s, 6.35, 1.45, 3.15, [
        ("date(2015, 3, 1)", "psycopg laver Pythons date om til DATE."),
        ("Tom tabel efter fejl?", "seed() er én transaction. Fejler trin 2, rulles trin 1 tilbage."),
        ("API'et kører ikke?", "load_patients() bruger en kopi af patient.yml."),
    ], card_h=0.98, gap=0.1, body_size=11)


def slide_step4():
    s = new_slide()
    title(s, "Trin 4.2: patients_at_hospital", "Test i pgAdmin først, kopiér derefter ind som t-string")
    code_box(s, 0.5, 1.45, 5.6, 2.1,
             "query = t\"\"\"\n"
             "    SELECT p.first_name, p.last_name, d.doctor_name\n"
             "    FROM patient AS p\n"
             "    JOIN doctor AS d ON d.doctor_id = p.doctor_id\n"
             "    WHERE d.hospital_id = {hospital_id}\n"
             "    ORDER BY p.last_name\n"
             "\"\"\"", size=11)
    hint_cards(s, 6.35, 1.45, 3.15, [
        ("Kun to tabeller", "hospital_id står allerede i doctor."),
        ("ON", "patient.doctor_id peger på doctor.doctor_id."),
    ], card_h=0.95, gap=0.15)
    text(s, 0.5, 3.8, 9, 1.0,
         [[("✅ Tjek: ", {"bold": True, "color": GOOD}),
           ("6 patienter på Rigshospitalet: Berg, Holm, Juhl, Kellerman, Larsson, Lund. "
            "Derefter NotImplementedError: trin 5.3.", {})]], size=14)


def slide_step5():
    s = new_slide()
    title(s, "Trin 5: GROUP BY i queries.py",
          "5.1 GROUP BY id → 5.2 JOIN → 5.3 LEFT JOIN → 5.5 løn per speciale")
    code_box(s, 0.5, 1.45, 5.6, 1.55,
             "SELECT h.hospital_name,\n"
             "       COUNT(d.doctor_id) AS doctors\n"
             "FROM hospital AS h\n"
             "LEFT JOIN doctor AS d ON d.hospital_id = h.hospital_id\n"
             "GROUP BY h.hospital_name\n"
             "ORDER BY doctors DESC, h.hospital_name", size=10)
    code_box(s, 0.5, 3.15, 5.6, 1.5,
             "SELECT speciality,\n"
             "       COUNT(*)             AS doctors,\n"
             "       AVG(salary)::integer AS avg_salary,\n"
             "       MAX(salary)          AS max_salary\n"
             "FROM doctor\n"
             "GROUP BY speciality ORDER BY speciality", size=10)
    hint_cards(s, 6.35, 1.45, 3.15, [
        ("hospital til venstre", "LEFT JOIN beholder alle rækker fra tabellen i FROM."),
        ("COUNT(d.doctor_id)", "Bornholm: 0. Med COUNT(*) ville det være 1."),
        ("5.4 bryd reglen", "Tilføj d.doctor_name i SELECT, og læs fejlen."),
    ], card_h=0.98, gap=0.1, body_size=11)


def slide_step6():
    s = new_slide()
    title(s, "Trin 6: HAVING med en t-string", "En værdi i HAVING er en parameter, præcis som i WHERE")
    code_box(s, 0.5, 1.45, 5.6, 1.5,
             "query = t\"\"\"\n"
             "    SELECT speciality, COUNT(*) AS doctors\n"
             "    FROM doctor\n"
             "    GROUP BY speciality\n"
             "    HAVING COUNT(*) >= {min_doctors}\n"
             "    ORDER BY doctors DESC\n"
             "\"\"\"", size=10)
    code_box(s, 0.5, 3.1, 5.6, 0.75,
             "HAVING AVG(salary) > {min_avg_salary}", size=11)
    hint_cards(s, 6.35, 1.45, 3.15, [
        ("6.2 WHERE COUNT(*)", "fejler: grupperne findes ikke endnu ved WHERE."),
        ("6.3 begge dele", "WHERE hospital_id = 1 (række) + HAVING AVG(salary) > 60000 (gruppe)."),
    ], card_h=1.1, gap=0.15, body_size=11)
    text(s, 0.5, 4.1, 9, 0.8,
         [[("✅ Tjek: ", {"bold": True, "color": GOOD}),
           ("6.1 → ('Kardiologi', 3).  6.4 → ('Ortopædkirurgi', 71000) og ('Kardiologi', 66333).", {})]],
         size=14)


def slide_errors():
    s = new_slide()
    title(s, "Almindelige fejl og hvad de betyder")
    table(s, 0.5, 1.2, [4.6, 4.4], [
        ["Du ser", "Det betyder"],
        ["ForeignKeyViolation … is not present", "FK peger på noget, der ikke findes (endnu)"],
        ["ForeignKeyViolation … still referenced", "andre rækker peger stadig på den"],
        ["must appear in the GROUP BY clause", "kolonne i SELECT er hverken grupperet eller aggregeret"],
        ["aggregate functions are not allowed in WHERE", "brug HAVING i stedet"],
        ["column reference \"hospital_id\" is ambiguous", "skriv d.hospital_id eller h.hospital_id"],
        ["function … does not exist", "kør procedures.sql i pgAdmin først"],
        ["RaiseException: Ingen læger …", "din egen RAISE EXCEPTION, som tilsigtet"],
    ], size=11, row_h=0.45, mono_cols=(0,))


# --- Afslutning ------------------------------------------------------------------------


def slide_links():
    s = new_slide()
    title(s, "Læs mere", "Alle links står også nederst i theory.md")
    groups = [
        ("Relationships", [
            ("Foreign keys", "https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-FK"),
            ("Tutorial: foreign keys", "https://www.postgresql.org/docs/current/tutorial-fk.html"),
            ("Date/time types", "https://www.postgresql.org/docs/current/datatype-datetime.html"),
            ("pgAdmin ERD Tool", "https://www.pgadmin.org/docs/pgadmin4/latest/erd_tool.html"),
        ]),
        ("JOIN og GROUP BY", [
            ("Tutorial: joins", "https://www.postgresql.org/docs/current/tutorial-join.html"),
            ("Tutorial: aggregates", "https://www.postgresql.org/docs/current/tutorial-agg.html"),
            ("GROUP BY og HAVING",
             "https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-GROUP"),
            ("W3Schools: JOIN", "https://www.w3schools.com/sql/sql_join.asp"),
            ("W3Schools: HAVING", "https://www.w3schools.com/sql/sql_having.asp"),
        ]),
        ("Stored procedures", [
            ("CREATE FUNCTION", "https://www.postgresql.org/docs/current/sql-createfunction.html"),
            ("CREATE PROCEDURE", "https://www.postgresql.org/docs/current/sql-createprocedure.html"),
            ("PL/pgSQL: IF og FOUND",
             "https://www.postgresql.org/docs/current/plpgsql-control-structures.html"),
            ("PL/pgSQL: RAISE",
             "https://www.postgresql.org/docs/current/plpgsql-errors-and-messages.html"),
            ("psycopg: errors", "https://www.psycopg.org/psycopg3/docs/api/errors.html"),
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
        ('4', 'JOIN', 'queries.py', 7),
        ('5', 'GROUP BY', 'LEFT JOIN + COUNT', 9),
        ('6', 'HAVING', 'WHERE vs HAVING', 6),
        ('7', 'Procedures', 'SELECT + CALL', 8),
    ], [
        [('Skriv SQL i pgAdmin først. ', {"bold": True, "color": DARK}),
         ('Når resultatet er rigtigt, kopierer du det over i '
          'Python.', {})],
        [('Sidder du fast? ', {"bold": True, "color": DARK}),
         ('1) læs fejlen nedefra og op  2) læs TODO-hintet  3) find '
          'slidet for trinnet  4) kig i solution/', {})],
        [('Færdig før tid? ', {"bold": True, "color": DARK}),
         ('Ekstraopgaver: tre tabeller i én query, år med EXTRACT, '
          'move_doctor, many-to-many.', {})],
    ])


def main() -> None:
    use_part(2)
    slide_title()
    slide_plan()
    slide_why()
    section(1, "Relationships og foreign keys", "ER diagram → CREATE TABLE → seed (trin 1–3)")
    slide_erd()
    slide_fk_side()
    slide_given_sql()
    slide_references()
    slide_order()
    slide_pgadmin()
    section(2, "JOIN, GROUP BY og HAVING", "Sæt tabellerne sammen, og regn på grupper")
    slide_join()
    slide_left_join()
    slide_aggregates()
    slide_group_by()
    slide_group_rule()
    slide_having()
    section(3, "Stored procedures", "FUNCTION og PROCEDURE: kode, der bor i databasen")
    slide_function_vs_procedure()
    slide_function_anatomy()
    slide_procedure()
    slide_call_from_python()
    slide_pros_cons()
    section(4, "Sådan løser du trin 3–7", "Mønstre, hints og de tjek, du skal kigge efter")
    slide_step3()
    slide_step4()
    slide_step5()
    slide_step6()
    slide_errors()
    slide_links()
    slide_roadmap()
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else OUT
    try:
        save(out, "Del 2 - Hospitaler, JOIN, GROUP BY og stored procedures")
    except PermissionError:
        sys.exit(f"Kan ikke skrive {out}. Luk den i PowerPoint, og kør igen.")
    print(f"skrev {out}")


if __name__ == "__main__":
    main()
