# CLAUDE.md — Pigeon Repository Guide

This file provides AI assistants with a comprehensive overview of the Pigeon repository: its structure, development workflows, and conventions.

## Repository Overview

**Pigeon** is a polyglot portfolio/experimentation monorepo containing multiple independent projects across different tech stacks. Each subdirectory is a self-contained project with its own dependencies, tests, and tooling.

## Project Map

| Project | Path | Stack | Purpose |
|---------|------|-------|---------|
| ag-grid-dsl | `ag-grid-dsl/ag-grid-dsl/` | TypeScript, React, Vite | DSL for generating rich data tables from markdown |
| tally | `tally/tally/` | Python, Django | Budget tracking web app |
| whisper | `whisper/` | Python | GPU-accelerated audio transcription via faster-whisper |
| snake | `snake/` | Vanilla JS, HTML, CSS | Classic snake game |
| plant-demo | `sim/plant-demo/` | Python, pytest | Plant life simulation |
| disc-rip | `automation/disc-rip/` | Python | Windows MakeMKV disc ripping automation |
| orbit | `orbit/` | Python, numpy | Orbital mechanics calculations |
| equations_of_motion | `equations_of_motion.py` | Python | 3D projectile physics utilities |

## Directory Structure

```
pigeon/
├── CLAUDE.md                        # This file
├── README.md                        # Top-level project overview
├── __init__.py                      # Root Python package init
├── equations_of_motion.py           # 3D projectile physics
├── ag-grid-dsl/
│   └── ag-grid-dsl/                 # TypeScript/React DSL project
│       ├── src/
│       │   ├── App.tsx              # Main React component
│       │   ├── Table.tsx            # Table rendering component
│       │   ├── TableDefinitionParser.ts  # Markdown-to-table parser
│       │   ├── table_definition.md  # Example DSL definition
│       │   └── test/               # Vitest tests
│       ├── package.json
│       ├── vite.config.ts
│       ├── tsconfig.json
│       └── eslint.config.js
├── automation/
│   └── disc-rip/
│       ├── disc_rip.py             # MakeMKV automation (Windows)
│       └── .env.example            # Config template
├── orbit/
│   └── test_orbits.py              # Gravity/orbital calculations
├── sim/
│   └── plant-demo/
│       ├── main.py                 # Simulation entry point
│       ├── class_defs.py           # Plant, Day, Weather classes
│       ├── functions.py            # Simulation logic
│       ├── tests/                  # pytest suite
│       ├── pyproject.toml
│       └── .python-version         # Python 3.14
├── snake/
│   ├── script.js                   # Game engine
│   ├── test_script.js              # Unit tests
│   ├── index.html
│   ├── run_tests.html              # Browser test runner
│   └── styles.css
├── tally/
│   └── tally/
│       ├── manage.py
│       ├── budget/                 # Django app
│       │   ├── models.py           # Category, BudgetCategoryMonthlyLimit, Transaction
│       │   ├── views.py
│       │   ├── forms.py
│       │   ├── urls.py
│       │   ├── admin.py
│       │   ├── tests.py
│       │   └── migrations/
│       └── tally/                  # Django project settings
└── whisper/
    ├── fast_audio_example.py       # CUDA-accelerated transcription
    ├── processor.py
    ├── device_selector.py
    ├── music_transcription.py
    ├── helpers/
    └── requirements.txt
```

## Development Commands

### ag-grid-dsl (TypeScript/React)

Working directory: `ag-grid-dsl/ag-grid-dsl/`

```bash
npm run dev      # Dev server with HMR
npm run build    # TypeScript compile + Vite bundle → dist/
npm run lint     # ESLint
npm run test     # Vitest (watch mode)
npm run preview  # Preview production build
```

### tally (Django)

Working directory: `tally/tally/`

```bash
python manage.py runserver    # Dev server (port 8000)
python manage.py test         # Run Django tests
python manage.py migrate      # Apply migrations
python manage.py makemigrations budget  # Generate new migrations
```

### plant-demo (Python/uv)

Working directory: `sim/plant-demo/`

```bash
pytest           # Run tests
python main.py   # Run simulation
uv sync          # Install dependencies
```

Requires Python 3.14+. Uses `uv` as the package manager.

### snake (Vanilla JS)

Working directory: `snake/`

```bash
python3 -m http.server 8000   # Serve locally; open http://localhost:8000
```

Tests run in-browser by opening `run_tests.html`.

### whisper (Python)

Working directory: `whisper/`

```bash
pip install -r requirements.txt
python fast_audio_example.py    # Run transcription (requires CUDA GPU)
```

### disc-rip (Python)

Working directory: `automation/disc-rip/`

```bash
cp .env.example .env            # Configure paths
python disc_rip.py              # Start automation (Windows only)
python disc_rip.py --clear-batch  # Reset TV show batch state
```

### orbit / equations_of_motion (Python)

```bash
python orbit/test_orbits.py
python equations_of_motion.py
```

## Testing Summary

| Project | Framework | How to Run |
|---------|-----------|-----------|
| ag-grid-dsl | Vitest + @testing-library/react | `npm test` in `ag-grid-dsl/ag-grid-dsl/` |
| tally | Django test framework | `python manage.py test` in `tally/tally/` |
| plant-demo | pytest | `pytest` in `sim/plant-demo/` |
| snake | Vanilla JS assertions | Open `run_tests.html` in a browser |
| whisper | pytest | `pytest` in `whisper/` |
| orbit | pytest | `pytest orbit/test_orbits.py` |

## Key Conventions

### Python

- **plant-demo** uses **Python 3.14+** and `uv` for dependency management. Do not use `pip` directly for this project.
- **tally** uses Django ORM; all schema changes must go through migrations (`makemigrations` + `migrate`).
- **whisper** depends on CUDA — tests/runs requiring GPU will fail on CPU-only machines.
- **disc-rip** is Windows-only (uses `subprocess` calls to MakeMKV and Windows drive letters).

### TypeScript / React

- **ag-grid-dsl** targets React 19 and ag-grid-react 34.
- Uses Vite 7 with a custom markdown loader plugin (raw `.md` files imported as strings).
- ESLint enforces React hooks rules and TypeScript strict mode. Run `npm run lint` before committing.
- Tests use Vitest with jsdom; component tests use `@testing-library/react`.

### JavaScript (snake)

- Vanilla JS only — no frameworks or build steps.
- Tests are assertion-based functions in `test_script.js`, driven by `run_tests.html`.

### Git

- Default branch: `main`
- Feature work happens on branches; PRs merge into `main`.
- Commit messages tend to be concise and feature-focused.
- `.gitignore` excludes: `*.pyc`, `*.sqlite3`, `env/`, `node_modules/`.

## Environment / Configuration

- **tally** (`settings.py`): Uses SQLite, `DEBUG=True`, and a placeholder `SECRET_KEY`. Do not ship to production without changing these.
- **disc-rip**: Copy `.env.example` → `.env` and configure MakeMKV paths, output directories, and polling intervals before running.
- **whisper**: No `.env` file; CUDA device is selected via `device_selector.py`.

## Architecture Notes

### ag-grid-dsl

The core idea is a DSL where a markdown table definition file (`table_definition.md`) is parsed by `TableDefinitionParser.ts` into a structured config consumed by `Table.tsx` (an ag-grid wrapper). This lets non-engineers define complex table layouts in plain text.

### tally

Standard Django MVT app. Data model: `Category` → `BudgetCategoryMonthlyLimit` (per-month budget cap) → `Transaction` (individual spend records). Views are class-based where possible.

### whisper

Audio is chunked in `processor.py`, then fed to `faster-whisper` (CTranslate2 backend) running on a CUDA GPU. `device_selector.py` enumerates PyAudio input devices for live recording. `music_transcription.py` adds post-processing tailored for lyrics.

### plant-demo

OOP simulation: a `Plant` object (with water/sunlight thresholds) is stepped through `Day` objects (with `Weather`). The `live_a_day` function determines growth or death. Tests are in `tests/test_main.py` using pytest.

### disc-rip

Watches for disc insertion on Windows, invokes MakeMKV via subprocess, classifies output as film or TV episode, then moves/renames the resulting MKV files. TV episodes batch across multiple discs.

## What This Repo Is Not

- Not a single deployable application — each subdirectory is an independent experiment.
- No shared library or internal package — projects do not import from each other.
- No CI/CD pipeline configured (no `.github/workflows/`, no `Makefile`).
