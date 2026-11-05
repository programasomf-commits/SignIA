import os
from pathlib import Path

from dotenv import load_dotenv


# Cargar las variables privadas desde backend/.env
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_FILE)

# Obtener y validar el umbral de confianza
try:
    UMBRAL_CONFIANZA = float(os.getenv("SIGNIA_UMBRAL", "0.85"))
except ValueError as exc:
    raise RuntimeError(
        "SIGNIA_UMBRAL debe ser un numero entre 0 y 1."
    ) from exc

if not 0 <= UMBRAL_CONFIANZA <= 1:
    raise RuntimeError(
        "SIGNIA_UMBRAL debe estar entre 0 y 1."
    )
