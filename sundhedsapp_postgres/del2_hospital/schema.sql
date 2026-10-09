-- Del 2, trin 2: opret hospital, doctor og patient.
-- Kør i pgAdmin: højreklik på sundhedsapp-databasen -> Query Tool -> indsæt -> F5.
--
-- Udgangspunktet fra opgaven ser sådan ud:
--
--   CREATE TABLE Hospital (
--       Hospital_Id INTEGER NOT NULL PRIMARY KEY,
--       Hospital_Name TEXT NOT NULL,
--       Bed_Count INTEGER NOT NULL
--   );
--   CREATE TABLE Doctor (
--       Doctor_Id INTEGER NOT NULL PRIMARY KEY,
--       Doctor_Name TEXT NOT NULL,
--       Hospital_Id INTEGER NOT NULL,
--       Joining_Date TEXT NOT NULL,
--       Speciality TEXT NOT NULL,
--       Salary INTEGER NOT NULL,
--       Experience INTEGER
--   );
--
-- Det virker, men i trin 1.5 fandt du fire svagheder. Her retter vi dem:
--   1. Doctor.Hospital_Id er bare et tal. Intet stopper hospital 99.  -> REFERENCES
--   2. Joining_Date er TEXT, så '2024-13-45' og 'i går' accepteres.   -> DATE
--   3. Vi skal selv finde på alle id'er.                              -> GENERATED ALWAYS AS IDENTITY
--   4. Blandet Store_Og_Små. PostgreSQL laver dem alligevel om til små bogstaver -> snake_case
--
-- ADVARSEL: dette sletter patient-tabellen fra del 1 og laver en ny med en doctor_id.

DROP TABLE IF EXISTS patient, doctor, hospital;

-- Færdig: brug den som model.
CREATE TABLE hospital (
    hospital_id    INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    hospital_name  TEXT    NOT NULL UNIQUE,
    bed_count      INTEGER NOT NULL CHECK (bed_count >= 0)
);

CREATE TABLE doctor (
    doctor_id      INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    doctor_name    TEXT    NOT NULL,
    -- TODO 2.2: tilføj hospital_id: INTEGER NOT NULL REFERENCES hospital (hospital_id),
    -- TODO 2.3: tilføj joining_date med typen DATE (ikke TEXT) og NOT NULL
    speciality     TEXT    NOT NULL,
    salary         INTEGER NOT NULL CHECK (salary > 0),
    experience     INTEGER CHECK (experience >= 0)  -- NULL betyder "ukendt"
);

-- Patient-tabellen fra del 1, plus en læge.
CREATE TABLE patient (
    patient_id  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    first_name  TEXT    NOT NULL,
    last_name   TEXT    NOT NULL,
    age         INTEGER NOT NULL CHECK (age BETWEEN 0 AND 150),
    blood_type  TEXT    NOT NULL
        CHECK (blood_type IN ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-')),
    allergies   TEXT    -- NULL betyder "ingen kendte allergier"
    -- TODO 2.4: tilføj doctor_id, der er påkrævet og peger på doctor (doctor_id).
    --           Husk kommaet efter allergies TEXT, når den ikke længere er sidste kolonne.
);
