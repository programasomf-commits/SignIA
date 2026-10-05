from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Configuración de conexión a PostgreSQL
DATABASE_URL = "postgresql+psycopg2://postgres:qwerty.12345@localhost:5432/signia_db"

# Motor de conexión
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