import cv2
import mediapipe as mp
import math
import json
from pathlib import Path
from datetime import datetime

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


print("======================================")
print("       SIGNIA - CAPTURA DATASET")
print("======================================")

print("OpenCV:", cv2.__version__)
print("MediaPipe:", mp.__version__)


# --------------------------------------------------
# 1. Configuración
# --------------------------------------------------

MODEL_PATH = "models/hand_landmarker.task"

NUM_FRAMES = 30

DATASET_DIR = Path("data/raw")

DATASET_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# --------------------------------------------------
# 2. Solicitar etiqueta
# --------------------------------------------------

print()
print("Ejemplo de etiquetas:")
print("HOLA")
print("GRACIAS")
print("BUENOS_DIAS")
print()

label = input(
    "Escribe la etiqueta de la seña que vas a realizar: "
).strip().upper()


if not label:

    print("ERROR: Debes escribir una etiqueta.")

    exit()


print()
print("Etiqueta seleccionada:", label)


# --------------------------------------------------
# 3. Configuración de MediaPipe
# --------------------------------------------------

base_options = python.BaseOptions(
    model_asset_path=MODEL_PATH
)

options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)


detector = vision.HandLandmarker.create_from_options(
    options
)

print("Detector de manos listo.")


# --------------------------------------------------
# 4. Determinar número de muestra
# --------------------------------------------------

archivos_existentes = list(
    DATASET_DIR.glob(
        f"LSM-{label}-*.json"
    )
)

numero_muestra = len(archivos_existentes) + 1

sample_id = (
    f"LSM-{label}-{numero_muestra:03d}"
)


print("ID de muestra:", sample_id)


# --------------------------------------------------
# 5. Abrir cámara
# --------------------------------------------------

cap = cv2.VideoCapture(0)

if not cap.isOpened():

    print(
        "ERROR: No se pudo abrir la cámara."
    )

    detector.close()

    exit()


print()
print("Cámara iniciada.")
print()
print("INSTRUCCIONES")
print("--------------------------------------")
print("1. Coloca tu mano frente a la cámara.")
print("2. Realiza la seña:", label)
print("3. Presiona ESPACIO.")
print("4. Mantén la seña/movimiento durante")
print("   los 30 frames.")
print("5. ESC cancela.")
print("--------------------------------------")


# --------------------------------------------------
# 6. Función de normalización
# --------------------------------------------------

def normalizar_landmarks(hand_landmarks):

    wrist = hand_landmarks[0]

    puntos = []

    for landmark in hand_landmarks:

        x = landmark.x - wrist.x
        y = landmark.y - wrist.y
        z = landmark.z - wrist.z

        puntos.append(
            (x, y, z)
        )


    max_distancia = 0.0

    for x, y, z in puntos:

        distancia = math.sqrt(
            x ** 2 +
            y ** 2 +
            z ** 2
        )

        if distancia > max_distancia:

            max_distancia = distancia


    if max_distancia == 0:

        return puntos


    puntos_normalizados = []

    for x, y, z in puntos:

        puntos_normalizados.append(
            (
                x / max_distancia,
                y / max_distancia,
                z / max_distancia
            )
        )


    return puntos_normalizados


# --------------------------------------------------
# 7. Variables
# --------------------------------------------------

secuencia = []

capturando = False

frame_timestamp_ms = 0

frames_capturados = 0


# --------------------------------------------------
# 8. Bucle de cámara
# --------------------------------------------------

while True:

    ret, frame = cap.read()

    if not ret:

        print(
            "ERROR: No se pudo leer la cámara."
        )

        break


    frame = cv2.flip(frame, 1)


    # BGR -> RGB

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )


    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )


    frame_timestamp_ms += 33


    # Detectar manos

    result = detector.detect_for_video(
        mp_image,
        frame_timestamp_ms
    )


    # --------------------------------------------------
    # Captura de secuencia
    # --------------------------------------------------

    if capturando:

        if result.hand_landmarks:

            hand_landmarks = result.hand_landmarks[0]


            puntos_normalizados = (
                normalizar_landmarks(
                    hand_landmarks
                )
            )


            secuencia.append(
                puntos_normalizados
            )


            frames_capturados += 1


            print(
                f"Frame {frames_capturados}/"
                f"{NUM_FRAMES}"
            )


            if frames_capturados >= NUM_FRAMES:

                capturando = False


                print()
                print(
                    "======================================"
                )

                print(
                    "CAPTURA COMPLETADA"
                )

                print(
                    "======================================"
                )


    # --------------------------------------------------
    # Dibujar landmarks
    # --------------------------------------------------

    if result.hand_landmarks:

        hand_landmarks = result.hand_landmarks[0]

        height, width, _ = frame.shape


        for landmark in hand_landmarks:

            x = int(
                landmark.x * width
            )

            y = int(
                landmark.y * height
            )


            cv2.circle(
                frame,
                (x, y),
                5,
                (0, 255, 0),
                -1
            )


    # --------------------------------------------------
    # Texto
    # --------------------------------------------------

    if capturando:

        texto = (
            f"{label} | "
            f"{frames_capturados}/"
            f"{NUM_FRAMES}"
        )

    else:

        texto = (
            f"{label} | "
            "ESPACIO = Capturar"
        )


    cv2.putText(
        frame,
        texto,
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )


    cv2.imshow(
        "SignIA - Captura Dataset",
        frame
    )


    # --------------------------------------------------
    # Teclas
    # --------------------------------------------------

    key = cv2.waitKey(1) & 0xFF


    # ESPACIO

    if key == 32 and not capturando:

        secuencia = []

        frames_capturados = 0

        capturando = True


        print()
        print(
            "======================================"
        )

        print(
            "INICIANDO CAPTURA"
        )

        print(
            "Etiqueta:",
            label
        )

        print(
            "ID:",
            sample_id
        )

        print(
            "======================================"
        )


    # ESC

    if key == 27:

        break


# --------------------------------------------------
# 9. Liberar cámara
# --------------------------------------------------

cap.release()

cv2.destroyAllWindows()

detector.close()


# --------------------------------------------------
# 10. Guardar muestra
# --------------------------------------------------

if len(secuencia) == NUM_FRAMES:

    datos = {

        "sample_id": sample_id,

        "label": label,

        "language": "LSM",

        "frames": len(secuencia),

        "landmarks_per_frame": 21,

        "coordinates_per_landmark": 3,

        "shape": [
            len(secuencia),
            21,
            3
        ],

        "normalization": {
            "origin": "wrist_landmark_0",
            "scale": "maximum_euclidean_distance"
        },

        "created_at": (
            datetime.now().isoformat()
        ),

        "sequence": secuencia
    }


    output_file = (
        DATASET_DIR /
        f"{sample_id}.json"
    )


    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            datos,
            file,
            ensure_ascii=False,
            indent=2
        )


    print()
    print(
        "======================================"
    )

    print(
        "MUESTRA GUARDADA CORRECTAMENTE"
    )

    print(
        "======================================"
    )

    print(
        "Archivo:",
        output_file
    )

    print(
        "Etiqueta:",
        label
    )

    print(
        "Muestra:",
        sample_id
    )

    print(
        "Frames:",
        len(secuencia)
    )

    print(
        "Forma:",
        (len(secuencia), 21, 3)
    )


else:

    print()
    print(
        "No se guardó la muestra."
    )

    print(
        f"Frames capturados: "
        f"{len(secuencia)}/{NUM_FRAMES}"
    )


print()
print(
    "Programa finalizado."
)