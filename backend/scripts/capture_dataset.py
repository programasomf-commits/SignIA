import csv
import json
import sys
from datetime import datetime
from pathlib import Path

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

BASE = Path(__file__).resolve().parents[2]
DATA_DIR = BASE / "data"
RAW_DIR = DATA_DIR / "raw"
CSV_PATH = DATA_DIR / "labels" / "dataset_master.csv"
MODEL_PATH = BASE / "models" / "hand_landmarker.task"

def main():
    label = input("Glosa de la seña (ej. HOLA): ").strip().upper()
    persona = input("Identificador real del participante (ej. P01): ").strip()

    if not label or not persona:
        print("ERROR: la glosa y el participante son obligatorios.")
        return

    if not MODEL_PATH.exists():
        print(f"ERROR: no existe el modelo detector: {MODEL_PATH}")
        return

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)

    existentes = list(RAW_DIR.glob(f"LSM-{label}-*.json"))
    numeros = []
    for archivo in existentes:
        try:
            numeros.append(int(archivo.stem.rsplit("-", 1)[1]))
        except (ValueError, IndexError):
            pass

    numero = max(numeros, default=0) + 1
    sample_id = f"LSM-{label}-{numero:03d}"
    output = RAW_DIR / f"{sample_id}.json"

    if output.exists():
        print(f"ERROR: ya existe {output}; no se sobrescribirá.")
        return

    base = python.BaseOptions(model_asset_path=str(MODEL_PATH))
    options = vision.HandLandmarkerOptions(
        base_options=base,
        running_mode=vision.RunningMode.IMAGE,
        num_hands=1,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5
    )

    detector = vision.HandLandmarker.create_from_options(options)
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        detector.close()
        print("ERROR: no se pudo abrir la cámara.")
        return

    landmarks = None
    print("Coloca la mano y presiona ESPACIO para capturar.")
    print("Presiona ESC para salir sin guardar.")

    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                print("ERROR: no se pudo leer la cámara.")
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            result = detector.detect(mp_image)

            landmarks = None
            if result.hand_landmarks:
                hand = result.hand_landmarks[0]
                landmarks = [[float(p.x), float(p.y), float(p.z)] for p in hand]
                for p in hand:
                    cv2.circle(frame, (int(p.x * frame.shape[1]),
                                      int(p.y * frame.shape[0])),
                               4, (0, 255, 0), -1)

            cv2.putText(frame, f"{label} | {persona} | ESPACIO captura",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        (0, 255, 0), 2)
            cv2.imshow("SignIA - Captura estatica", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == 27:
                print("Captura cancelada.")
                return
            if key == 32:
                if landmarks is None or len(landmarks) != 21:
                    print("No se detectaron 21 landmarks. Intenta de nuevo.")
                    continue
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()
        detector.close()

    datos = {
        "sample_id": sample_id,
        "label": label,
        "language": "LSM",
        "persona_id": persona,
        "landmarks": landmarks,
        "landmarks_count": 21,
        "coordinates_per_landmark": 3,
        "normalization": "raw_mediapipe_coordinates",
        "created_at": datetime.now().isoformat()
    }

    with output.open("x", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

    filas = []
    if CSV_PATH.exists():
        with CSV_PATH.open(newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames and {"ruta_archivo", "glosa", "persona_id"}.issubset(reader.fieldnames):
                filas = list(reader)

    ruta_relativa = f"raw/{output.name}"
    filas.append({
        "ruta_archivo": ruta_relativa,
        "glosa": label,
        "persona_id": persona
    })

    temporal = CSV_PATH.with_suffix(".tmp")
    with temporal.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["ruta_archivo", "glosa", "persona_id"])
        writer.writeheader()
        writer.writerows(filas)
    temporal.replace(CSV_PATH)

    print(f"Muestra guardada: {output}")
    print(f"Participante: {persona} | Glosa: {label}")
    print(f"CSV actualizado: {CSV_PATH}")

if __name__ == "__main__":
    main()
