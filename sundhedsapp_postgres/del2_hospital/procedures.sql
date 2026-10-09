-- Del 2, trin 7: en function og en procedure.
-- Kør i pgAdmin: højreklik på sundhedsapp-databasen -> Query Tool -> indsæt -> F5.
-- CREATE OR REPLACE betyder, at du kan køre filen igen, hver gang du har ændret den.
--
-- FUNCTION  returnerer data     -> kaldes med SELECT * FROM navn(...)
-- PROCEDURE udfører en handling -> kaldes med CALL navn(...)

-- 7.1 Function (færdig): alle læger med et bestemt speciale, bedst betalte først.
--     Læs den linje for linje. Koden mellem $$ og $$ er en helt almindelig SELECT.
CREATE OR REPLACE FUNCTION doctors_by_speciality(p_speciality TEXT)
RETURNS TABLE (doctor_name TEXT, hospital_name TEXT, salary INTEGER)
LANGUAGE sql
AS $$
    SELECT d.doctor_name, h.hospital_name, d.salary
    FROM doctor AS d
    JOIN hospital AS h ON h.hospital_id = d.hospital_id
    WHERE d.speciality = p_speciality
    ORDER BY d.salary DESC;
$$;

-- 7.3 Procedure: giv alle læger med et speciale en lønstigning i procent.
CREATE OR REPLACE PROCEDURE raise_salary(p_speciality TEXT, p_percent INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
    -- TODO 7.3: skriv en UPDATE på doctor, der sætter
    --           salary = salary + salary * p_percent / 100
    --           for de læger, hvor speciality = p_speciality.
    --           Husk semikolon efter UPDATE-statementet.

    -- FOUND er true, hvis UPDATE ændrede mindst én række.
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Ingen læger med specialet %', p_speciality;
    END IF;
END;
$$;

-- Prøv i Query Tool:
--   SELECT * FROM doctors_by_speciality('Kardiologi');
--   CALL raise_salary('Pædiatri', 10);
--   CALL raise_salary('Tandlæge', 10);   -- skal fejle med din egen besked
