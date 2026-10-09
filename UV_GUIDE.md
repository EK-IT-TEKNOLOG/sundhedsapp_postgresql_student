# Kort guide til uv

[uv](https://docs.astral.sh/uv/) er ét værktøj, der erstatter `pip`, `venv` og `pyenv`. Det installerer
pakker, opretter virtuelle miljøer og kører dine scripts, og det er meget hurtigt.

## Installér uv

**Windows (PowerShell):**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS / Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Luk og åbn terminalen igen, og tjek at det virker:

```bash
uv --version
```

Mangler du Python 3.14, kan uv installere den: `uv python install 3.14`.

## De vigtigste filer

| Fil | Hvad det er |
|---|---|
| `pyproject.toml` | Projektets pakker og Python-version. Den redigerer du (eller `uv add`) |
| `uv.lock` | De præcise versioner, der blev installeret. Commit den, men redigér den ikke selv |
| `.venv/` | Det virtuelle miljø. Oprettes af `uv sync`. Commit den **ikke** |

## De kommandoer, du skal bruge

Kør dem fra mappen med `pyproject.toml` (her: `sundhedsapp_postgres`).

| Kommando | Hvad den gør |
|---|---|
| `uv sync` | Opretter `.venv` og installerer alle pakker fra `uv.lock`. Kør den efter `git clone` og `git pull` |
| `uv run crud.py` | Kører et script i projektets miljø. Du behøver ikke aktivere `.venv` |
| `uv run python` | Starter en Python-shell med projektets pakker |
| `uv run pytest` | Kører et værktøj, der er installeret i projektet |
| `uv run flask --app app run` | Starter en Flask-app |
| `uv add requests` | Tilføjer en pakke til `pyproject.toml` og installerer den |
| `uv add --dev pytest` | Tilføjer en pakke, der kun bruges under udvikling (fx tests) |
| `uv remove requests` | Fjerner en pakke igen |
| `uv run --with pandas script.py` | Kører et script med en ekstra pakke, uden at tilføje den til projektet |

`uv run` virker fra undermapper også: uv finder selv `pyproject.toml` længere oppe.

## Typisk arbejdsgang

```bash
git clone <repo-url>
cd <repo-mappe>/sundhedsapp_postgres
uv sync                       # én gang, og igen efter git pull
cd del1_database_crud
uv run crud.py                # kør dine øvelser
```

## VS Code

Vælg projektets miljø, så VS Code kan finde pakkerne og køre koden:
`Ctrl+Shift+P` → *Python: Select Interpreter* → vælg den med `.venv`.

## Almindelige fejl

| Fejl | Løsning |
|---|---|
| `uv: command not found` / `uv genkendes ikke` | Luk og åbn terminalen efter installationen |
| `No module named 'psycopg'` | Kør `uv sync`, og start scriptet med `uv run` i stedet for `python` |
| `No pyproject.toml found` | Du står i en forkert mappe. Gå til `sundhedsapp_postgres` eller en undermappe |
| VS Code viser røde streger under imports | Vælg `.venv`-interpreteren (se ovenfor) |
| `requires-python >=3.14` | Kør `uv python install 3.14` og derefter `uv sync` |

## Hvis du kender pip

| pip / venv | uv |
|---|---|
| `python -m venv .venv` + `pip install -r requirements.txt` | `uv sync` |
| `pip install requests` | `uv add requests` |
| `.venv\Scripts\activate` + `python app.py` | `uv run app.py` |

Mere: [uv-dokumentationen](https://docs.astral.sh/uv/getting-started/features/).
