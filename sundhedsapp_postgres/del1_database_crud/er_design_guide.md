# Sådan designer du et ER diagram, trin for trin

Et ER diagram er en **plan**: du tænker over data, *før* du skriver SQL. At ændre en
tegning tager sekunder. At ændre en tabel fuld af data er meget sværere.

Denne guide viser en metode i **7 trin** og gennemgår den på `patient.yml` fra lektion 4.
Brug samme metode i del 2, hvor du tilføjer hospitaler og læger.

---

## Byggestenene

| Ord | Betydning | Bliver i SQL til | Eksempel |
|---|---|---|---|
| **Entity** | En *ting*, vi gemmer data om. Som regel et navneord. | en tabel | patient, hospital, doctor |
| **Attribute** | En oplysning om entity'en | en kolonne | age, blood_type |
| **Primary key (PK)** | Den attribute, der identificerer præcis én række | `PRIMARY KEY` | patient_id |
| **Foreign key (FK)** | En attribute, der peger på en PK i en anden tabel | `REFERENCES` | doctor.hospital_id |
| **Relationship** | Hvordan to entities hænger sammen | en foreign key | en læge *arbejder på* et hospital |
| **Cardinality** | *Hvor mange* på hver side af et relationship | hvor FK'en placeres | ét hospital har **mange** læger |

### Crow's foot notation (bruges af pgAdmin)

Enderne af en relationship-linje viser cardinality:

```
  ──||──   præcis én             ──|<──   én eller flere
  ──o|──   nul eller én          ──o<──   nul eller flere  ("crow's foot")
```

```
  HOSPITAL ──||────────o<── DOCTOR
  "ét hospital har nul eller flere læger, hver læge arbejder på præcis ét hospital"
```

I del 1 har vi kun **én** entity, så der er endnu ingen relationships. De kommer i del 2.

---

## Trin 1: Indsaml de data, du skal gemme

Se på de rigtige data, og skriv alle felter ned. Vores kilde er `patient.yml`:

```yaml
patients:
  id:
    1:
      age: 34
      allergies: false
      blood_type: O+
      first_name: Kevin
      last_name: Holm
```

**Felter:** `id`, `age`, `allergies`, `blood_type`, `first_name`, `last_name`

> 💡 Se også på den kode, der *skriver* data. API'et fra lektion 4 `/add_patient` bruger key'en
> `bloodtype` (uden underscore). Forskellige navne for det samme er et klassisk dataproblem,
> og en database med ét fast kolonnenavn løser det.

## Trin 2: Find entities

Spørg dig selv: **hvilke *ting* handler disse felter om?** Alle seks felter beskriver én patient,
så vi har én entity: **patient**.

Navngivningsregler, vi følger:

- små bogstaver, ord adskilt med `_` (`blood_type`, ikke `BloodType`)
- en tabel navngives i **ental**: `patient`, ikke `patients`. Én række er én patient.

## Trin 3: Find attributes, og vælg en data type til hver

Se på værdierne for hvert felt, og spørg: **er det et tal eller tekst? Skal jeg regne eller sortere med det?**

| Felt | Eksempelværdier | Data type | Hvorfor |
|---|---|---|---|
| first_name | Kevin, Lone | `TEXT` | fritekst |
| last_name | Holm, Kellerman | `TEXT` | fritekst |
| age | 34, 66, 27 | `INTEGER` | et heltal, vi vil sortere og sammenligne |
| blood_type | O+, A+, B- | `TEXT` | tekst fra en kort, fast liste |
| allergies | false, Peanuts, 'No' | `TEXT` | tekst, *efter rensning* (se trin 5) |

> 💡 **Bedre design (diskussion):** alder ændrer sig hvert år. Et rigtigt system gemmer `birth_date DATE`
> og beregner alderen. Vi beholder `age` for at matche data fra lektion 4.

## Trin 4: Vælg primary key

En god primary key er:

1. **unik**: ingen to rækker deler den
2. **aldrig tom** (aldrig NULL)
3. **stabil**: den ændrer sig aldrig

Kunne `first_name + last_name` være key'en? Nej, for to patienter kan hedde *Kevin Holm*.
Et CPR-nummer er unikt, men det er følsomme persondata og bør ikke spredes rundt som key.

Så vi tilføjer en **surrogate key**: et tal uden betydning, genereret af databasen:

```sql
patient_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY
```

YAML dict key'en `1:` gjorde det samme, men `len(new) + 1` i lektion 4 laver dubletter,
når en patient er blevet slettet. `IDENTITY` genbruger aldrig et nummer.

## Trin 5: Beslut, hvad der er påkrævet (NULL eller NOT NULL)

Spørg for hver kolonne: **kan en patient eksistere uden denne værdi?**

| Kolonne | Påkrævet? | Beslutning |
|---|---|---|
| first_name, last_name | ja | `NOT NULL` |
| age | ja | `NOT NULL` |
| blood_type | ja (i vores app) | `NOT NULL` |
| allergies | nej, mange har ingen | nullable |

**Én betydning per værdi.** YAML-filen bruger tre forskellige måder at sige "ingen allergier" på:
`false`, `'No'` og `'no'`. I databasen vælger vi **én**: `NULL` betyder "ingen kendte allergier".
Når vi importerer data, *renser* vi dem, så de følger den regel.

## Trin 6: Tilføj regler (constraints)

Hvilke værdier giver ingen mening? Lad databasen afvise dem:

| Kolonne | Regel | SQL |
|---|---|---|
| age | mellem 0 og 150 | `CHECK (age BETWEEN 0 AND 150)` |
| blood_type | én af 8 blodtyper | `CHECK (blood_type IN ('A+','A-','B+','B-','AB+','AB-','O+','O-'))` |

## Trin 7: Tjek designet (normalisering light)

Stil disse tre spørgsmål om hver kolonne:

1. **Én værdi per celle?** Hvis en patient har *to* allergier, bryder `allergies = 'Peanuts, Strawberry'`
   denne regel, og du kan ikke let søge efter "alle, der er allergiske over for jordnødder".
   Løsningen er en separat `allergy`-tabel (én patient, mange allergier). Det er en *ekstraopgave*.
2. **Er noget gemt to gange?** For eksempel kan `age` og `birth_date` side om side være uenige.
3. **Beskriver hver kolonne *denne* entity?** En kolonne som `hospital_name` hører ikke
   hjemme i `patient`. Den hører til i sin egen tabel (del 2).

---

## Resultatet

```
┌───────────────────────────────────┐
│ patient                           │
├────┬──────────────┬───────────────┤
│ PK │ patient_id   │ integer       │
│    │ first_name   │ text          │
│    │ last_name    │ text          │
│    │ age          │ integer       │
│    │ blood_type   │ text          │
│    │ allergies    │ text  (null)  │
└────┴──────────────┴───────────────┘
```

---

## Tegn det i pgAdmin 9.18 (ERD Tool)

1. I **Object Explorer**, højreklik på databasen `sundhedsapp`, og vælg **ERD For Database**.
   (Du kan også markere databasen og bruge **Tools → ERD Tool**.)
2. Klik på knappen **Add table** (tabelikonet med et `+`) i værktøjslinjen.
3. Fanen **General**: Name = `patient`, Schema = `public`.
4. Fanen **Columns**: klik **+** én gang for hver kolonne:
   - Name, Data type (`integer` eller `text`)
   - Kontakten **Not NULL?**: slået til for alle kolonner undtagen `allergies`
   - Kontakten **Primary key?**: slået til for `patient_id`
5. For `patient_id`: åbn kolonnen (blyantikonet), gå til **Constraints**, og sæt
   Type = **IDENTITY** og Identity = **ALWAYS**.
6. Klik **Save** i dialogen. Tabellen vises på lærredet.
7. Klik **Generate SQL** (SQL-ikonet i værktøjslinjen). pgAdmin åbner et Query Tool med
   `CREATE TABLE`-koden. Sammenlign den med din `schema.sql`.
8. Gem diagrammet med **Save**-ikonet som `patient.pgerd` i øvelsesmappen.

> 💡 pgAdmins ERD Tool tilføjer ikke `CHECK` constraints for dig. Tilføj dem i `schema.sql` (trin 2
> i øvelsen).

I del 2 bruger du **One-to-Many** (relationship-knappen i værktøjslinjen) til at forbinde
`doctor` med `hospital`.

---

## Læs mere

- [pgAdmin: ERD Tool](https://www.pgadmin.org/docs/pgadmin4/latest/erd_tool.html). Den officielle guide til alle knapper.
- [Lucidchart: What is an ER diagram?](https://www.lucidchart.com/pages/er-diagrams). En god, visuel introduktion med crow's foot notation.
- [PostgreSQL: Identity columns](https://www.postgresql.org/docs/current/ddl-identity-columns.html)
- [PostgreSQL: Constraints](https://www.postgresql.org/docs/current/ddl-constraints.html)
- [PostgreSQL: Data types](https://www.postgresql.org/docs/current/datatype.html)
- [Mermaid: ER diagrams in Markdown](https://mermaid.js.org/syntax/entityRelationshipDiagram.html). Tegn ER diagrammer som tekst i VS Code eller på GitHub.
