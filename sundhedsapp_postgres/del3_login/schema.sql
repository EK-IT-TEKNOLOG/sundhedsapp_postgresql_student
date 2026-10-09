-- Del 3, trin 2: tabellerne fra del 2 plus role og app_user.
-- Kør i pgAdmin: højreklik på sundhedsapp-databasen -> Query Tool -> indsæt -> F5.
-- Kør derefter data.sql for at fylde hospital, doctor og patient.
--
-- ADVARSEL: dette sletter og genopretter alle tabeller fra del 1 og 2.

DROP TABLE IF EXISTS app_user, role, patient, doctor, hospital;

-- --- Fra del 2 (færdig) ---------------------------------------------------------

CREATE TABLE hospital (
    hospital_id    INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    hospital_name  TEXT    NOT NULL UNIQUE,
    bed_count      INTEGER NOT NULL CHECK (bed_count >= 0)
);

CREATE TABLE doctor (
    doctor_id      INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    doctor_name    TEXT    NOT NULL,
    hospital_id    INTEGER NOT NULL REFERENCES hospital (hospital_id),
    joining_date   DATE    NOT NULL,
    speciality     TEXT    NOT NULL,
    salary         INTEGER NOT NULL CHECK (salary > 0),
    experience     INTEGER CHECK (experience >= 0)  -- NULL betyder "ukendt"
);

CREATE TABLE patient (
    patient_id  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    first_name  TEXT    NOT NULL,
    last_name   TEXT    NOT NULL,
    age         INTEGER NOT NULL CHECK (age BETWEEN 0 AND 150),
    blood_type  TEXT    NOT NULL
        CHECK (blood_type IN ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-')),
    allergies   TEXT,   -- NULL betyder "ingen kendte allergier"
    doctor_id   INTEGER NOT NULL REFERENCES doctor (doctor_id)
);

-- --- Nyt i del 3: login og roller -----------------------------------------------

-- TODO 2.2: opret tabellen role med
--             role_id    genereret primary key (som hospital_id)
--             role_name  påkrævet tekst, og to roller må ikke have samme navn (UNIQUE)


-- TODO 2.3: indsæt de tre roller 'admin', 'doctor' og 'nurse' med ét INSERT-statement:
--           INSERT INTO role (role_name) VALUES (...), (...), (...);


-- "user" er et reserveret ord i PostgreSQL, så tabellen hedder app_user.
CREATE TABLE app_user (
    user_id        INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username       TEXT    NOT NULL UNIQUE
    -- TODO 2.4: tilføj tre kolonner (husk kommaet efter username-linjen):
    --   password_hash  påkrævet tekst. Aldrig selve passwordet!
    --   role_id        påkrævet, peger på role (role_id)
    --   doctor_id      må være NULL (kun læger har en), peger på doctor (doctor_id),
    --                  og UNIQUE: én læge kan højst have én bruger
);
