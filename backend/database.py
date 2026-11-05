import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

# Cargar las variables privadas desde backend/.env
ENV_FILE = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_FILE)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "Falta DATABASE_URL. Verifica el archivo backend/.env."
    )


def get_connection():
    """Abre una conexion PostgreSQL usando DATABASE_URL."""
    return psycopg.connect(DATABASE_URL)
