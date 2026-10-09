-- Del 4 (fra del 3): hospitaler, læger og patienter fra del 2 (færdig).
-- Kør efter schema.sql i pgAdmin: Query Tool -> indsæt -> F5.
-- Brugerne oprettes ikke her, men af users.py, fordi passwords skal hashes i Python.

INSERT INTO hospital (hospital_name, bed_count) VALUES
    ('Rigshospitalet', 1100),                -- 1
    ('Aarhus Universitetshospital', 1150),   -- 2
    ('Odense Universitetshospital', 1000),   -- 3
    ('Aalborg Universitetshospital', 600),   -- 4
    ('Bornholms Hospital', 90);              -- 5

INSERT INTO doctor (doctor_name, hospital_id, joining_date, speciality, salary, experience) VALUES
    ('Mette Sørensen', 1, '2015-03-01', 'Kardiologi', 72000, 12),        -- 1
    ('Jonas Madsen', 1, '2021-08-15', 'Kardiologi', 58000, 4),           -- 2
    ('Sara Nielsen', 1, '2019-01-10', 'Pædiatri', 61000, 7),             -- 3
    ('Ali Hassan', 2, '2012-06-01', 'Ortopædkirurgi', 78000, 15),        -- 4
    ('Emma Kristensen', 2, '2023-02-01', 'Pædiatri', 52000, NULL),       -- 5
    ('Peter Larsen', 2, '2017-09-01', 'Kardiologi', 69000, 9),           -- 6
    ('Freja Andersen', 3, '2020-04-01', 'Ortopædkirurgi', 64000, 6),     -- 7
    ('Oliver Poulsen', 3, '2024-01-15', 'Almen medicin', 50000, NULL),   -- 8
    ('Ida Rasmussen', 4, '2016-11-01', 'Almen medicin', 60000, 10);      -- 9

-- De fire første er patienterne fra patient.yml i lektion 4.
INSERT INTO patient (first_name, last_name, age, blood_type, allergies, doctor_id) VALUES
    ('Kevin', 'Holm', 34, 'O+', NULL, 1),
    ('Lone', 'Kellerman', 66, 'A+', 'Peanuts', 2),
    ('Lars', 'Larsson', 27, 'B-', 'Strawberry', 3),
    ('Mel', 'Holm', 34, 'O-', NULL, 4),
    ('Sofie', 'Berg', 8, 'A+', NULL, 3),
    ('Noah', 'Friis', 5, 'O+', 'Gluten', 5),
    ('Karen', 'Lund', 71, 'A-', NULL, 1),
    ('Henrik', 'Dahl', 58, 'B+', 'Penicillin', 6),
    ('Maja', 'Krogh', 45, 'AB+', NULL, 4),
    ('Anders', 'Bech', 39, 'O+', NULL, 7),
    ('Laura', 'Vinther', 29, 'O-', 'Pollen', 9),
    ('Erik', 'Juhl', 82, 'A+', NULL, 1);
