import csv
import json
import shutil
import sys
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import LeaveOneGroupOut, cross_val_score

BASE = Path(__file__).resolve().parents[2]
DATA_DIR = BASE / "data"
CSV_PATH = DATA_DIR / "labels" / "dataset_master.csv"
MODEL_PATH = BASE / "backend" / "app" / "ml_models" / "modelo_lenguaje_senas.pkl"

sys.path.insert(0, str(BASE / "backend"))
from app.services.features import normalizar_landmarks

def cargar():
    X, y, personas = [], [], []
    omitidas = []

    if not CSV_PATH.exists():
        raise FileNotFoundError(f"No existe el CSV: {CSV_PATH}")

    with CSV_PATH.open(newline="", encoding="utf-8-sig") as f:
        for fila in csv.DictReader(f):
            ruta_relativa = (fila.get("ruta_archivo") or "").strip()
            glosa = (fila.get("glosa") or "").strip()
            persona = (fila.get("persona_id") or "").strip()

            if not ruta_relativa or not glosa or not persona:
                omitidas.append(fila.get("ruta_archivo", "(sin ruta)"))
                continue

            ruta = DATA_DIR / ruta_relativa.replace("/", str(Path("/")))
            if not ruta.exists():
                omitidas.append(f"{ruta_relativa}: archivo no encontrado")
                continue

            try:
                with ruta.open(encoding="utf-8") as g:
                    datos = json.load(g)

                puntos = datos.get("landmarks")
                if puntos is None:
                    omitidas.append(f"{ruta_relativa}: contiene sequence, no landmarks estáticos")
                    continue

                vector = normalizar_landmarks(puntos)
                if len(vector) != 63 or not np.isfinite(vector).all():
                    omitidas.append(f"{ruta_relativa}: landmarks inválidos")
                    continue

                X.append(vector)
                y.append(glosa)
                personas.append(persona)
            except (OSError, ValueError, TypeError, KeyError) as exc:
                omitidas.append(f"{ruta_relativa}: {exc}")

    if omitidas:
        print(f"Muestras omitidas por datos incompatibles o incompletos: {len(omitidas)}")
        for item in omitidas[:10]:
            print(" -", item)

    return np.asarray(X), np.asarray(y), np.asarray(personas)

def main():
    X, y, personas = cargar()
    clases = set(y.tolist())
    grupos = set(personas.tolist())
    print(f"Muestras válidas: {len(y)} | Clases: {len(clases)} | Personas: {len(grupos)}")

    if len(y) == 0:
        print("No hay muestras estáticas válidas. Usa capture_dataset.py para capturarlas.")
        return

    if len(grupos) < 3:
        print("Se necesitan al menos 3 personas para evaluar con una persona fuera.")
        print("No se entrenó ni se reemplazó ningún modelo.")
        return

    if len(clases) < 2:
        print("Se necesitan al menos dos clases distintas para entrenar.")
        return

    clasificador = RandomForestClassifier(n_estimators=200, random_state=42)
    cv = LeaveOneGroupOut()
    puntajes = cross_val_score(clasificador, X, y, groups=personas, cv=cv)

    print("Exactitud por persona dejada fuera:", np.round(puntajes, 3))
    print(f"Exactitud media: {puntajes.mean():.3f}")

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    if MODEL_PATH.exists():
        respaldo = MODEL_PATH.with_name(
            f"{MODEL_PATH.stem}.bak_{__import__('datetime').datetime.now():%Y%m%d_%H%M%S}{MODEL_PATH.suffix}"
        )
        shutil.copy2(MODEL_PATH, respaldo)
        print(f"Modelo anterior respaldado en: {respaldo}")

    clasificador.fit(X, y)
    joblib.dump(clasificador, MODEL_PATH)
    print(f"Modelo guardado en: {MODEL_PATH}")

if __name__ == "__main__":
    main()
