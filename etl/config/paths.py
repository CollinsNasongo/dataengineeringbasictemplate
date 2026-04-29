from pathlib import Path
import os

# =========================
# BASE DATA DIRECTORY
# =========================
DATA_DIR = Path(os.getenv("DATA_DIR", Path(__file__).resolve().parent.parent.parent / "data"))

# =========================
# LAYER DIRECTORIES
# =========================
LANDING_DIR = DATA_DIR / "landing"
BRONZE_DIR = DATA_DIR / "bronze"
SILVER_DIR = DATA_DIR / "silver"
GOLD_DIR   = DATA_DIR / "gold"

# =========================
# FILE HELPERS
# =========================
def landing_file(filename: str) -> Path:
    return LANDING_DIR / filename

def bronze_file(filename: str) -> Path:
    return BRONZE_DIR / filename

def silver_file(filename: str) -> Path:
    return SILVER_DIR / filename

def gold_file(filename: str) -> Path:
    return GOLD_DIR / filename


# =========================
# DEBUG HELPER
# =========================
def debug_paths():
    print("DATA_DIR  :", DATA_DIR)
    print("LANDING_DIR:", LANDING_DIR)
    print("BRONZE_DIR:", BRONZE_DIR)
    print("SILVER_DIR:", SILVER_DIR)
    print("GOLD_DIR  :", GOLD_DIR)