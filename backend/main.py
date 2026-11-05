from pathlib import Path
import json
import os
from dotenv import load_dotenv


from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.database import get_connection
from backend.app.api.v1.endpoints.predict import router as predict_router
from backend.app.db.database import Base, engine
from backend.app.models.dataset_master import DatasetMuestra
from backend.app.models.registro_prediccion import RegistroPrediccion

app = FastAPI(
    title="SignIA API",
    description="API backend para el proyecto SignIA",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

app.include_router(predict_router)

# Cargar variables de entorno del backend
ENV_FILE = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_FILE)

# Obtener los origenes autorizados para CORS
cors_origins = os.getenv(
    "SIGNIA_CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173"
)

ALLOWED_ORIGINS = [
    origin.strip()
    for origin in cors_origins.split(",")
    if origin.strip()
]

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "data" / "raw"


@app.get("/")
def root():
    return {
        "proyecto": "SignIA",
        "mensaje": "API funcionando correctamente",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "SignIA API"
    }


@app.get("/dataset")
def get_dataset():
    samples = []

    for file in sorted(DATASET_DIR.glob("*.json")):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)

            samples.append({
                "sample_id": data.get("sample_id"),
                "label": data.get("label"),
                "language": data.get("language"),
                "shape": data.get("shape"),
                "file": file.name
            })

        except (json.JSONDecodeError, OSError):
            continue

    return {
        "total_samples": len(samples),
        "samples": samples
    }

@app.get("/dataset/summary")
def get_dataset_summary():
    labels = set()
    languages = set()
    total_samples = 0

    for file in sorted(DATASET_DIR.glob("*.json")):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)

            total_samples += 1

            if data.get("label"):
                labels.add(data.get("label"))

            if data.get("language"):
                languages.add(data.get("language"))

        except (json.JSONDecodeError, OSError):
            continue

    return {
        "total_samples": total_samples,
        "labels": sorted(labels),
        "languages": sorted(languages)
    }
@app.get("/dataset/{sample_id}")
def get_sample(sample_id: str):
    # Validar el identificador para evitar acceso a otras rutas
    if not sample_id or not sample_id.replace("-", "").replace("_", "").isalnum():
        raise HTTPException(
            status_code=400,
            detail="Identificador de muestra no valido."
        )

    file_path = DATASET_DIR / f"{sample_id}.json"

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail=f"Muestra no encontrada: {sample_id}"
        )

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

    except (json.JSONDecodeError, OSError):
        raise HTTPException(
            status_code=500,
            detail="No fue posible leer correctamente la muestra."
        )

    return {
        "sample_id": data.get("sample_id", sample_id),
        "label": data.get("label"),
        "language": data.get("language"),
        "frames": data.get("frames"),
        "landmarks_per_frame": data.get("landmarks_per_frame"),
        "coordinates_per_landmark": data.get("coordinates_per_landmark"),
        "shape": data.get("shape")
    }

@app.get("/database/status")
def database_status():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT 1;")
        cursor.fetchone()

        return {
            "status": "ok"
        }

    except Exception:
        return {
            "status": "error"
        }

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()
