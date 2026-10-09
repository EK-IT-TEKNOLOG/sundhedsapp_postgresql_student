# Del 3 – Teori: login, passwords, tokens og role-based access control

Læs dette før undervisningen (ca. 35 minutter). Slides'ene `del3_theory.pptx` dækker de samme
emner og viser, hvordan du løser hvert trin i øvelsen.

---

## 1. Hvad var problemet i lektion 4?

I lektion 4 kunne man få et bearer token sådan her:

```
POST /token/1   ->   {"token": "Bearer eyJ..."}
```

Der var **intet password**. Alle, der kunne gætte tallet 1, fik et gyldigt token. Og når man
havde et token, måtte man **alt**. Sundhedsdata er blandt de mest følsomme data, der findes, så
det holder ikke. I del 3 løser vi to problemer:

| Spørgsmål | Fagord | HTTP-svar, når svaret er nej |
|---|---|---|
| **Hvem er du?** Bevis det med brugernavn og password. | **Authentication** | `401 Unauthorized` |
| **Hvad må du?** En sygeplejerske må ikke slette patienter. | **Authorization** | `403 Forbidden` |

> 💡 Husk forskellen: **401** = "jeg ved ikke, hvem du er" (log ind). **403** = "jeg ved godt, hvem
> du er, men du må ikke" (at logge ind igen hjælper ikke).

## 2. Brugere og roller i databasen

Vi udvider ER diagrammet fra del 2 med to tabeller:

```
role  1 ──< mange  app_user  0..1 ──── 0..1  doctor
```

```sql
CREATE TABLE role (
    role_id    INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    role_name  TEXT    NOT NULL UNIQUE
);

CREATE TABLE app_user (
    user_id        INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username       TEXT    NOT NULL UNIQUE,
    password_hash  TEXT    NOT NULL,
    role_id        INTEGER NOT NULL REFERENCES role (role_id),
    doctor_id      INTEGER UNIQUE REFERENCES doctor (doctor_id)
);
```

Tre ting at lægge mærke til:

- **Hvorfor `app_user` og ikke `user`?** `user` er et *reserveret ord* i PostgreSQL
  (`SELECT user;` giver navnet på den bruger, du er forbundet som). Man *kan* skrive `"user"` i
  anførselstegn, men så skal man huske dem overalt. Vælg et andet navn.
- **Én rolle per bruger:** `role_id` er en helt almindelig one-to-many, som i del 2. En rolle har
  mange brugere, og en bruger har én rolle.
- **One-to-one med `UNIQUE`:** en bruger med rollen `doctor` er knyttet til én række i `doctor`.
  `UNIQUE` på foreign key'en gør relationship'et til **one-to-one**: én læge kan højst have én
  bruger. `NULL` er tilladt, fordi admin og sygeplejersker ikke er læger. (Flere `NULL`-værdier
  bryder ikke `UNIQUE`.)

**Hvorfor en `role`-tabel og ikke bare en tekstkolonne?** Med en tabel kan databasen afvise
`'admn'` (foreign key), og du kan senere tilføje kolonner til rollen, fx en beskrivelse.

## 3. Gem aldrig passwords: gem et hash

Hvis databasen bliver lækket (og det sker), må angriberen **ikke** kunne læse passwords. Folk
genbruger passwords, så et læk fra din app kan åbne deres e-mail og netbank.

Et **hash** er en envejsfunktion: det er nemt at regne `password → hash`, men umuligt at regne
baglæns. Ved login hasher vi det indtastede password igen og sammenligner.

```python
>>> from werkzeug.security import generate_password_hash, check_password_hash
>>> h = generate_password_hash("mette-pass")
>>> h
'scrypt:32768:8:1$jK0yzOuzAAhOfY4R$651b38ea62a3...'
>>> check_password_hash(h, "mette-pass")
True
>>> check_password_hash(h, "forkert")
False
```

Strengen indeholder tre dele, adskilt af `$`:

| Del | Eksempel | Betydning |
|---|---|---|
| Algoritme | `scrypt:32768:8:1` | hvilken hash-funktion og hvor "dyr" den er |
| **Salt** | `jK0yzOuzAAhOfY4R` | tilfældig tekst, ny for hvert password |
| Hash | `651b38ea…` | resultatet |

- **Salt:** kør `generate_password_hash("mette-pass")` to gange, og du får to forskellige hashes.
  Så kan en angriber ikke se, at to brugere har samme password, og kan ikke slå hashes op i en
  færdig tabel.
- **Langsom med vilje:** `scrypt` er designet til at tage tid og hukommelse. Én login mærker det ikke,
  men en angriber, der vil prøve milliarder af passwords, gør.

> ⚠️ Brug aldrig `hashlib.sha256(password)` til passwords. Den er lynhurtig og uden salt. Brug en
> funktion, der er lavet til passwords: `werkzeug.security` (følger med Flask), `argon2` eller `bcrypt`.

## 4. Login-flowet

```
 klient                                    server                          database
   │  POST /login {username, password}       │                                  │
   │ ──────────────────────────────────────> │  get_user_by_username()  ──────> │
   │                                         │  check_password_hash()           │
   │  {"token": "eyJ..."}                    │  create_token(user_id)           │
   │ <────────────────────────────────────── │                                  │
   │                                         │                                  │
   │  GET /patients                          │                                  │
   │  Authorization: Bearer eyJ...           │                                  │
   │ ──────────────────────────────────────> │  verify_token() -> get_user() ─> │
   │                                         │  rolle ok? ellers 403            │
   │  [ {...}, {...} ]                       │  all_patients()          ──────> │
   │ <────────────────────────────────────── │                                  │
```

Samme fejlbesked for forkert brugernavn og forkert password: `"Forkert brugernavn eller password"`.
Ellers kan en angriber finde ud af, hvilke brugernavne der findes.

## 5. JSON Web Tokens (JWT)

Tokenet er en **JWT**: tre base64-kodede dele adskilt af punktum.

```
eyJhbGciOiJIUzI1NiJ9 . eyJzdWIiOiIyIiwiZXhwIjoxNzkx...} . 3q9Xk2...
      header                        payload                  signatur
   {"alg": "HS256"}         {"sub": "2", "exp": 1791...}
```

| Claim | Betydning | Hos os |
|---|---|---|
| `sub` | *subject*: hvem tokenet handler om | brugerens `user_id` som tekst |
| `exp` | *expires*: udløbstid i sekunder siden 1970 | nu + 30 minutter |

- **Signaturen** er beregnet ud fra header, payload og serverens `SECRET_KEY`. Ændrer nogen ét tegn
  i payload, passer signaturen ikke længere, og tokenet afvises. Kun serveren kan lave gyldige tokens.
- **Payload er ikke krypteret!** Alle kan base64-dekode den og læse den (det prøver du i øvelsen).
  Læg aldrig passwords eller helbredsdata i et token.
- **`exp`** begrænser skaden, hvis et token bliver stjålet. Lektion 4's tokens udløb aldrig.
- **`SECRET_KEY`** laves tilfældigt, når serveren starter. Genstarter du serveren, er alle tokens
  ugyldige. I produktion læses nøglen fra en environment variabel.

Vi bruger biblioteket **joserfc**. Det er efterfølgeren til `authlib.jose` fra lektion 4 (samme
forfatter), og `authlib.jose` er nu markeret som forældet.

```python
payload = {"sub": str(user_id), "exp": int(time.time()) + 30 * 60}
token = jwt.encode({"alg": "HS256"}, payload, SECRET_KEY)      # lav

claims = jwt.decode(token, SECRET_KEY).claims                  # tjek signatur
REQUIRED_CLAIMS.validate(claims)                               # tjek exp
```

Begge fejl (forkert signatur og udløbet) er en `JoseError`, og så returnerer vi `None` → `401`.

**Hvorfor står rollen ikke i tokenet?** Vi slår brugeren op i databasen ved hver request. Det koster
én query, men hvis en admin fratager nogen rollen, virker det med det samme, og ikke først når
tokenet udløber.

> 💡 Ændring fra lektion 4: dér stod `"Bearer "` inde i selve tokenet. Standarden er, at serveren
> returnerer det rå token, og at **klienten** skriver `Authorization: Bearer <token>`. Swagger-siden
> `/docs` gør det for dig, når du klikker **Authorize**.

## 6. Role-based access control (RBAC)

Med **RBAC** giver man ikke rettigheder til personer, men til **roller**. Personer får en rolle.
Når Nina bliver ansat som sygeplejerske, får hun rollen `nurse` og dermed alt, hvad en sygeplejerske må.

Vores regler:

| Endpoint | admin | doctor | nurse | uden token |
|---|:---:|:---:|:---:|:---:|
| `POST /login` | ✅ | ✅ | ✅ | ✅ |
| `GET /me` | ✅ | ✅ | ✅ | 401 |
| `GET /patients` (alle) | ✅ | 403 | ✅ | 401 |
| `GET /my_patients` (egne) | 403 | ✅ | 403 | 401 |
| `DELETE /patients/<id>` | ✅ | 403 | 403 | 401 |

I APIFlask skriver man reglen direkte på endpointet:

```python
@app.get("/patients")
@app.auth_required(auth, roles=["admin", "nurse"])
def patients():
    return all_patients()
```

og fortæller én gang, hvordan man finder en brugers rolle:

```python
@auth.get_user_roles
def get_user_roles(user: dict) -> str:
    return user["role_name"]
```

To principper:

- **Least privilege:** giv hver rolle så få rettigheder som muligt. En læge behøver ikke se alle patienter.
- **Tjek altid på serveren.** At skjule en knap i en app beskytter ingenting: alle kan sende en
  request direkte med `requests` eller `curl`.

### Rolle er ikke nok: hvilke rækker?

Rollen `doctor` siger, at man må se *patienter*, men ikke *hvilke*. `/my_patients` bruger den
indloggede brugers `doctor_id` til at vælge rækkerne:

```python
return patients_of_doctor(auth.current_user["doctor_id"])
```

Id'et kommer fra tokenet (via databasen), **aldrig** fra et URL-parameter, som brugeren selv kan
ændre (`/patients_of_doctor/3`). Det kaldes adgang på række-niveau.

## 7. Rækker som dicts: `dict_row`

Et API sender JSON, og JSON har navne på felterne. Med `row_factory=dict_row` giver psycopg
rækker som dicts i stedet for tuples:

```python
from psycopg.rows import dict_row

with get_connection() as conn, conn.cursor(row_factory=dict_row) as cursor:
    cursor.execute(t"SELECT user_id, username FROM app_user WHERE user_id = {user_id}").fetchone()
    # {'user_id': 2, 'username': 'mette'}   i stedet for   (2, 'mette')
```

Flask laver en dict eller en liste af dicts om til JSON automatisk.

## 8. Tjekliste: sikkerhed

| ✅ Gør | ❌ Undgå |
|---|---|
| Gem kun `password_hash` | at gemme eller logge passwords |
| Samme fejl for forkert brugernavn og password | "Brugeren findes ikke" |
| `get_user()` uden `password_hash` | at sende hashet ud i et API-svar |
| Tokens med `exp` | tokens, der gælder for evigt |
| Vis `"Databasefejl"` til klienten, log detaljerne | at sende databasens fejlbesked til klienten |
| HTTPS i produktion | bearer tokens over almindelig HTTP (alle på netværket kan læse dem) |

---

### Test dig selv

1. Hvad er forskellen på authentication og authorization? Hvilken status code hører til hver?
2. Hvorfor hedder tabellen `app_user` og ikke `user`?
3. Hvad gør `UNIQUE` på `app_user.doctor_id` ved relationship'et?
4. Hvorfor giver `generate_password_hash("abc")` et nyt resultat hver gang? Hvordan kan login så virke?
5. Kan en bruger ændre `"sub": "2"` til `"sub": "1"` i sit token og blive admin? Hvorfor ikke?
6. Kan en bruger *læse* indholdet af sit token? Hvad betyder det for, hvad man må lægge i det?
7. Nina er sygeplejerske. Hvad svarer `GET /my_patients`, og hvorfor?
8. Hvorfor slår vi rollen op i databasen i stedet for at lægge den i tokenet?

---

## Læs mere

**Login og tokens**
- [APIFlask: Authentication](https://apiflask.com/authentication/). `HTTPTokenAuth`, `auth_required` og roller.
- [Flask-HTTPAuth: user roles](https://flask-httpauth.readthedocs.io/en/latest/#user-roles). `get_user_roles`, som APIFlask bygger på.
- [joserfc: JSON Web Token](https://jose.authlib.org/en/guide/jwt/)
- [RFC 7519: JSON Web Token](https://datatracker.ietf.org/doc/html/rfc7519). Afsnit 4.1 beskriver `sub` og `exp`.
- [MDN: 401 Unauthorized](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/401) og [403 Forbidden](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/403)

**Passwords og sikkerhed**
- [Werkzeug: generate_password_hash / check_password_hash](https://werkzeug.palletsprojects.com/en/stable/utils/#module-werkzeug.security)
- [OWASP: Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [OWASP: Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html). Se "Authentication and Error Messages".
- [OWASP: Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html). Least privilege og "deny by default".

**PostgreSQL og psycopg**
- [PostgreSQL: SQL key words](https://www.postgresql.org/docs/current/sql-keywords-appendix.html). `USER` er reserveret.
- [PostgreSQL: UNIQUE constraints](https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-UNIQUE-CONSTRAINTS). Også om NULL og UNIQUE.
- [psycopg: Row factories (dict_row)](https://www.psycopg.org/psycopg3/docs/advanced/rows.html)
