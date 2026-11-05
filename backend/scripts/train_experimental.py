import csv
import json
import sys
from pathlib import Path

import joblib
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

BASE = Path(__file__).resolve().parents[2]
DATA_DIR = BASE / "data"
CSV_PATH = DATA_DIR / "labels" / "dataset_master.csv"

MODEL_PATH = (
    BASE / "backend" / "app" / "ml_models" /
    "modelo_lenguaje_senas_experimental_P01.joblib"
)

sys.path.insert(0, str(BASE / "backend"))
from app.services.features import normalizar_landmarks


def cargar_datos():
    X, y = [], []
    omitidas = 0

    with CSV_PATH.open(newline="", encoding="utf-8-sig") as f:
        for fila in csv.DictReader(f):
            persona = (fila.get("persona_id") or "").strip().upper()
            glosa = (fila.get("glosa") or "").strip().upper()
            ruta_relativa = (fila.get("ruta_archivo") or "").strip()

            if persona != "P01":
                continue

            if glosa not in ("HOLA", "BUENOS_DIAS") or not ruta_relativa:
                continue

            ruta = DATA_DIR / ruta_relativa

            try:
                with ruta.open(encoding="utf-8") as archivo:
                    datos = json.load(archivo)

                puntos = datos.get("landmarks")

                if not isinstance(puntos, list) or len(puntos) != 21:
                    omitidas += 1
                    continue

                if not all(
                    isinstance(p, list)
                    and len(p) == 3
                    and all(
                        isinstance(v, (int, float))
                        and np.isfinite(v)
                        for v in p
                    )
                    for p in puntos
                ):
                    omitidas += 1
                    continue

                vector = normalizar_landmarks(puntos)

                if len(vector) != 63 or not np.isfinite(vector).all():
                    omitidas += 1
                    continue

                X.append(vector)
                y.append(glosa)

            except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
                omitidas += 1

    return np.asarray(X), np.asarray(y), omitidas


def main():
    print("\n======================================")
    print(" SIGNIA - ENTRENAMIENTO EXPERIMENTAL")
    print("======================================")

    X, y, omitidas = cargar_datos()

    print(f"Muestras válidas P01: {len(y)}")
    print(f"Muestras omitidas: {omitidas}")

    clases, cantidades = np.unique(y, return_counts=True)

    for clase, cantidad in zip(clases, cantidades):
        print(f"{clase}: {cantidad}")

    if len(y) < 10 or len(clases) < 2:
        print("No hay suficientes muestras para la prueba.")
        return

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )

    modelo = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced"
    )

    modelo.fit(X_train, y_train)

    predicciones = modelo.predict(X_test)

    print("\n=== RESULTADOS EXPERIMENTALES ===")
    print(f"Muestras de entrenamiento: {len(y_train)}")
    print(f"Muestras de prueba: {len(y_test)}")
    print(f"Exactitud: {accuracy_score(y_test, predicciones):.4f}")

    print("\n=== REPORTE DE CLASIFICACIÓN ===")
    print(classification_report(
        y_test,
        predicciones,
        zero_division=0
    ))

    print("=== MATRIZ DE CONFUSIÓN ===")
    print(confusion_matrix(
        y_test,
        predicciones,
        labels=modelo.classes_
    ))
    print("Orden de clases:", modelo.classes_.tolist())

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    if MODEL_PATH.exists():
        print("\nEl modelo experimental ya existe.")
        print("Se conservará una copia de seguridad.")

        respaldo = MODEL_PATH.with_name(
            f"{MODEL_PATH.stem}_respaldo.joblib"
        )

        if not respaldo.exists():
            import shutil
            shutil.copy2(MODEL_PATH, respaldo)

    joblib.dump(modelo, MODEL_PATH)

    print("\nModelo experimental actualizado:")
    print(MODEL_PATH)

    print("\nModelo experimental guardado:")
    print(MODEL_PATH)
    print("\nNOTA: evaluación con un solo participante (P01).")
    print("No demuestra generalización a otras personas.")


if __name__ == "__main__":
    main()
