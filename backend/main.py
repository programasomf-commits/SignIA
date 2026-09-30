from pathlib import Path
import json


from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.database import get_connection

app = FastAPI(
    title="SignIA API",
    description="API backend para el proyecto SignIA",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5175",
        "http://127.0.0.1:5175"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


DATASET_DIR = Path("data/raw")


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
    file_path = DATASET_DIR / f"{sample_id}.json"

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Muestra no encontrada: {sample_id}"
        )

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="El archivo JSON no tiene un formato valido."
        )

    return data

@app.get("/database/test")
def test_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, component, status FROM integration_test;"
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return {
        "status": "ok",
        "records": [
            {
                "id": row[0],
                "component": row[1],
                "status": row[2]
            }
            for row in rows
        ]
    }
