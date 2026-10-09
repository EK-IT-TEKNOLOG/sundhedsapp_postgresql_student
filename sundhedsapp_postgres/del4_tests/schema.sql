-- Del 4 (færdig fra del 3): hospital, doctor og patient fra del 2, plus role og app_user.
-- Kør i pgAdmin: højreklik på sundhedsapp-databasen -> Query Tool -> indsæt -> F5.
-- Kør derefter data.sql for at fylde hospital, doctor og patient.

DROP TABLE IF EXISTS app_user, role, patient, doctor, hospital;

-- --- Fra del 2 ------------------------------------------------------------------

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

-- Én række per rolle. Rollerne er faste, så vi indsætter dem her.
CREATE TABLE role (
    role_id    INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    role_name  TEXT    NOT NULL UNIQUE
);

INSERT INTO role (role_name) VALUES ('admin'), ('doctor'), ('nurse');

-- "user" er et reserveret ord i PostgreSQL, så tabellen hedder app_user.
CREATE TABLE app_user (
    user_id        INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username       TEXT    NOT NULL UNIQUE,
    password_hash  TEXT    NOT NULL,        -- aldrig selve passwordet
    role_id        INTEGER NOT NULL REFERENCES role (role_id),
    doctor_id      INTEGER UNIQUE REFERENCES doctor (doctor_id)  -- kun for læger, ellers NULL
);
