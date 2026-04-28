# General Data Engineering Template

A lightweight, production-ready, containerised data engineering template for end-to-end data projects. Built on Apache Airflow, PostgreSQL, and Metabase — designed to take a project from raw data to a live dashboard on a single machine.

> **Who this is for** — data engineers, analysts, and students who want a complete local data platform without cloud infrastructure. Ideal for portfolio projects, proofs of concept, small-team pipelines, and learning data engineering end-to-end.

---

## Getting Started

Apart from the prerequisites, **three steps are all you need to have a fully running data platform:**

### Step 1 — Clone and rename

```bash
git clone https://github.com/CollinsNasongo/general-data-engineering-template.git your-project-name
cd your-project-name
```

Rename the folder to match your project. Everything else is already in place.

### Step 2 — Configure your `.env`

```bash
cp .env.template .env
```

Generate your secrets:

```bash
python -c "
from cryptography.fernet import Fernet
import secrets
print('FERNET_KEY=' + Fernet.generate_key().decode())
print('AIRFLOW__API_AUTH__JWT_SECRET=' + secrets.token_hex(32))
print('AIRFLOW__WEBSERVER__SECRET_KEY=' + secrets.token_hex(32))
print('REDIS_PASSWORD=' + secrets.token_hex(32))
"
```

Paste the output into `.env`, then fill in your usernames, passwords, database name, and connection strings. That is the only configuration file you need to edit.

### Step 3 — Add a `.gitignore`

Create a `.gitignore` in the project root with at minimum:

```
.env
data/
logs/
```

This keeps your secrets and local data files out of version control.

### Step 4 — Create empty folders

Git does not track empty folders. Create the required directory structure with `.gitkeep` files so the folder layout is preserved in version control:

**Mac / Linux:**
```bash
touch dags/.gitkeep
touch data/bronze/.gitkeep
touch data/silver/.gitkeep
touch data/gold/.gitkeep
touch logs/.gitkeep
touch config/.gitkeep
touch plugins/.gitkeep
```

**Windows (PowerShell):**
```powershell
New-Item dags/.gitkeep -Force
New-Item data/bronze/.gitkeep -Force
New-Item data/silver/.gitkeep -Force
New-Item data/gold/.gitkeep -Force
New-Item logs/.gitkeep -Force
New-Item config/.gitkeep -Force
New-Item plugins/.gitkeep -Force
```

Then update your `.gitignore` to ignore folder contents but keep the `.gitkeep` files:

```
# Keep folder structure but ignore contents
data/bronze/*
data/silver/*
data/gold/*
logs/*
!data/bronze/.gitkeep
!data/silver/.gitkeep
!data/gold/.gitkeep
!logs/.gitkeep
```

### Step 5 — Start the platform

```bash
make reset
```

That's it. Airflow, Metabase, pgAdmin, Redis, and all three database layers will be up and running. See [Makefile Commands](#makefile-commands) for the full list of available commands.

> For subsequent changes — DAG edits, dependency updates, or full resets — see the [Redeployment Reference](#redeployment-reference).

| Service | URL |
|---|---|
| Airflow | http://localhost:8080 |
| Metabase | http://localhost:3000 |
| pgAdmin | http://localhost:5050 |

---

## Architecture

```
Sources → Orchestration (Airflow) → Storage (Bronze / Silver / Gold) → Visualisation (Metabase)
```

Data flows from any source through an Airflow-orchestrated ETL pipeline into a three-layer PostgreSQL data warehouse, then surfaces in Metabase for analysis and dashboarding.

---

## Stack

| Layer | Tool |
|---|---|
| Orchestration | Apache Airflow 3.x (CeleryExecutor) |
| Message broker | Redis |
| Data warehouse | PostgreSQL 16 (Bronze / Silver / Gold schemas) |
| Visualisation | Metabase v0.49.0 |
| DB admin UI | pgAdmin 4 |
| Containerisation | Docker Compose |

---

## Prerequisites

These are the only things you need to install before using the template:

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) — allocate at least 8 GB RAM and 4 CPUs in Settings → Resources (see [System Requirements](#system-requirements))
- Python 3.x — for generating secrets only
- `make` — see [Windows setup](#windows-setup-make) below

---

## System Requirements

This template runs entirely on a single machine via Docker.

| Tier | RAM | CPU | Disk | Use case |
|---|---|---|---|---|
| Minimum | 8 GB | 2 cores | 20 GB | Learning, small datasets (<100k rows) |
| Recommended | 16 GB | 4 cores | 40 GB | Development, medium datasets (<1M rows) |
| Comfortable | 32 GB | 8 cores | 80 GB | Heavy ETL, large datasets, multiple DAGs |

### Docker Desktop resource allocation

Set these in **Settings → Resources**:

| Setting | Minimum | Recommended |
|---|---|---|
| Memory | 8 GB | 12–16 GB |
| CPUs | 2 | 4+ |
| Disk image size | 20 GB | 40 GB |

### Per-container memory limits

| Container | Memory limit |
|---|---|
| airflow-worker | 2 GB |
| data-postgres | 2 GB |
| airflow-scheduler | 1 GB |
| airflow-apiserver | 1 GB |
| airflow-dag-processor | 1 GB |
| metabase | 1 GB |
| metabase-postgres | 1 GB |
| airflow-postgres | 1 GB |
| redis | 512 MB |
| **Total** | **~10.5 GB** |

> If your machine has less than 12 GB allocated to Docker, reduce the `mem_limit` on `airflow-worker` and `data-postgres` first.

### Disk space

| Item | Approximate size |
|---|---|
| Docker images (all services) | 4–6 GB |
| Built Airflow image | ~2 GB |
| PostgreSQL volumes | Depends on dataset size |
| Airflow logs | Grows over time — prune regularly with `make destroy` |

---

## Project Structure

```
project/
├── config/                        # Airflow config
├── dags/                          # Airflow DAG definitions
├── data/                          # Local data files (not committed)
│   ├── bronze/                    # Raw source files
│   ├── silver/                    # Intermediate files
│   └── gold/                      # Output files
├── etl/
│   ├── config/
│   │   └── paths.py               # Centralised path helpers
│   ├── extract/                   # Add source extraction logic here
│   ├── load/                      # Add database load logic here
│   ├── pipelines/                 # Add pipeline definitions here
│   ├── transform/                 # Add bronze / silver / gold transforms here
│   └── utils/                     # Add shared utilities here
├── logs/                          # Airflow logs (not committed)
├── .env                           # Secrets — never commit this
├── .env.template                  # Safe template to commit
├── .gitignore
├── docker-compose.yaml
├── Dockerfile
├── init.sql                       # Creates bronze / silver / gold schemas
├── Makefile
├── README.md
└── requirements.txt
```

---

## ETL Structure

The `etl/` package is organised by responsibility. Add your own logic into the relevant module — the folder structure is the convention, not the constraint.

**`etl/config/paths.py`** — centralised path helpers. All file paths resolve relative to the `data/` directory, or from the `DATA_DIR` environment variable when running inside Docker.

**`etl/extract/`** — source extraction logic. Add one file per source system.

**`etl/transform/`** — transformation logic split by layer. `bronze.py` handles raw ingestion, `silver.py` applies cleaning and business logic, `gold.py` builds aggregated output tables.

**`etl/load/`** — writes gold tables to the Postgres data warehouse.

**`etl/pipelines/`** — pipeline definitions that wire extract → transform → load together. Import these into your Airflow DAGs.

**`etl/utils/`** — shared utilities for logging and validation used across the pipeline.

> All Python files outside of `etl/config/paths.py` are starting points — modify, replace, or delete them to fit your project. `paths.py` should be kept as it centralises all path resolution for the pipeline.

---

## Data Layers

| Layer | Schema | Purpose |
|---|---|---|
| Bronze | `bronze` | Raw ingested data — no transformations |
| Silver | `silver` | Cleaned, typed, business logic applied |
| Gold | `gold` | Aggregated, modelled, ready for reporting |

The schemas are created automatically on first boot via `init.sql`.

---

## Makefile Commands

| Command | Description |
|---|---|
| `make up` | Start all services |
| `make down` | Stop all services |
| `make restart` | Restart scheduler and dag-processor (fast dev loop) |
| `make rebuild` | Rebuild image and restart (for dependency changes) |
| `make reset` | Full reset — wipes volumes and rebuilds from scratch |
| `make destroy` | Remove everything including images and orphaned volumes |
| `make logs` | Tail scheduler logs |
| `make logs service=airflow-worker` | Tail a specific service |
| `make ps` | Show running containers |
| `make metabase` | Open Metabase in browser |

---

## Connecting Metabase to Your Data

On first boot, open Metabase at `http://localhost:3000` and complete the setup wizard. When prompted to add a database:

- **Type:** PostgreSQL
- **Host:** `data-postgres`
- **Port:** `5432`
- **Database:** value of `DATA_POSTGRES_DB` in your `.env`
- **Username / Password:** values of `DATA_POSTGRES_USER` / `DATA_POSTGRES_PASSWORD`

---

## Connecting pgAdmin to Your Databases

Open pgAdmin at `http://localhost:5050` and log in with `PGADMIN_DEFAULT_EMAIL` and `PGADMIN_PASSWORD` from your `.env`. To register a server:

- **Host:** `data-postgres`
- **Port:** `5432`
- **Username / Password:** values of `DATA_POSTGRES_USER` / `DATA_POSTGRES_PASSWORD`

---

## Adding Dependencies

Any additional Python packages can be added to `requirements.txt` and will be installed into the Airflow image at build time. After adding a package, rebuild:

```bash
make rebuild
```

**Always pin versions** — e.g. `pandas==2.2.3` not `pandas`. Unpinned versions can silently break on the next build if a new release introduces incompatible changes.

Before adding a package, verify it is compatible with:
- **Python 3.13** — the version shipped with Airflow 3.x
- **The packages already in `requirements.txt`** — check for known conflicts, e.g. `numpy` and `pandas` versions must align

If a build fails after adding a package, check the error for version conflicts and adjust accordingly.

---

## Redeployment Reference

| Change | Action |
|---|---|
| DAG or ETL code | `make restart` |
| `requirements.txt` | `make rebuild` |
| `Dockerfile` | `make rebuild` |
| `.env` changes | `make down && make up` |
| Something is broken | `make reset` |
| Start fresh entirely | `make destroy && make reset` |

---

## Windows Setup (make)

Install `make` via winget:

```powershell
winget install GnuWin32.Make
```

Add to PATH permanently:

```powershell
[System.Environment]::SetEnvironmentVariable(
  "PATH",
  $env:PATH + ";C:\Program Files (x86)\GnuWin32\bin",
  "Machine"
)
```

Fully close and reopen VS Code. Verify with:

```powershell
$env:PATH -split ";" | Select-String "GnuWin"
```

---

## Debugging

### View logs

```bash
make logs
make logs service=airflow-worker
make logs service=airflow-dag-processor
```

### Common issues

**`ModuleNotFoundError`**
- Confirm `PYTHONPATH=/opt/airflow` is set in your compose environment
- Add `__init__.py` to all subdirectories under `etl/`

**DAG not appearing in the UI**
- Check dag-processor logs: `make logs service=airflow-dag-processor`
- Confirm the DAG file is inside `dags/` with no top-level import errors

**Build failures**
- Pin all versions in `requirements.txt`
- Run `make reset` to clear cached layers

**Database containers unhealthy**
- Wait 30 seconds — healthchecks retry up to 10 times
- Run `make ps` to check container status

**Out of memory**
- Increase Docker Desktop memory in Settings → Resources
- Reduce `mem_limit` on non-critical services in `docker-compose.yaml`

---

## Security Notes

- All secrets are managed via `.env` — never hardcoded
- Redis is password-protected
- Database ports are not exposed to the host
- Airflow and Metabase bind to `127.0.0.1` only
- `.env` is excluded from version control via `.gitignore`

---

## References & Acknowledgements

- [Apache Airflow](https://airflow.apache.org/) — workflow orchestration
- [Metabase](https://www.metabase.com/) — open-source BI and dashboarding
- [PostgreSQL](https://www.postgresql.org/) — open-source relational database
- [Redis](https://redis.io/) — in-memory message broker
- [pgAdmin](https://www.pgadmin.org/) — PostgreSQL administration UI
- [Docker](https://www.docker.com/) — containerisation platform

---

## Licence

MIT