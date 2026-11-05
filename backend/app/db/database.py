import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Cargar la configuracion privada desde backend/.env
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_FILE)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "Falta DATABASE_URL. Verifica que exista el archivo backend/.env."
    )

# Motor de conexion a PostgreSQL
engine = create_engine(
    DATABASE_URL,
    echo=False
)

# Gestor de sesiones
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Clase base para los modelos ORM
Base = declarative_base()


def get_db():
    """Proporciona una sesion de base de datos y la cierra al terminar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
