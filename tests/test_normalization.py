import cv2
import mediapipe as mp
import math

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


print("======================================")
print("     SIGNIA - NORMALIZACION LANDMARKS")
print("======================================")

print("OpenCV:", cv2.__version__)
print("MediaPipe:", mp.__version__)


# --------------------------------------------------
# 1. Ruta del modelo
# --------------------------------------------------

MODEL_PATH = "models/hand_landmarker.task"


# --------------------------------------------------
# 2. Configuración de MediaPipe
# --------------------------------------------------

base_options = python.BaseOptions(
    model_asset_path=MODEL_PATH
)

options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_hands=2,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)


# --------------------------------------------------
# 3. Crear detector
# --------------------------------------------------

detector = vision.HandLandmarker.create_from_options(
    options
)

print("Detector listo.")


# --------------------------------------------------
# 4. Abrir cámara
# --------------------------------------------------

cap = cv2.VideoCapture(0)

if not cap.isOpened():

    print("ERROR: No se pudo abrir la cámara.")

    detector.close()

    exit()


print("Cámara iniciada.")
print("Coloca una mano frente a la cámara.")
print("Presiona ESC para salir.")


frame_timestamp_ms = 0
ultimo_timestamp = -1


# --------------------------------------------------
# 5. Función de normalización
# --------------------------------------------------

def normalizar_landmarks(hand_landmarks):

    # Punto 0 = muñeca

    wrist = hand_landmarks[0]

    # ----------------------------------------------
    # Primera etapa:
    # trasladar el origen a la muñeca
    # ----------------------------------------------

    puntos = []

    for landmark in hand_landmarks:

        x = landmark.x - wrist.x
        y = landmark.y - wrist.y
        z = landmark.z - wrist.z

        puntos.append((x, y, z))


    # ----------------------------------------------
    # Segunda etapa:
    # calcular escala máxima
    # ----------------------------------------------

    max_distancia = 0.0

    for x, y, z in puntos:

        distancia = math.sqrt(
            x ** 2 +
            y ** 2 +
            z ** 2
        )

        if distancia > max_distancia:

            max_distancia = distancia


    # Evitar división entre cero

    if max_distancia == 0:

        return puntos


    # ----------------------------------------------
    # Tercera etapa:
    # escalar los puntos
    # ----------------------------------------------

    puntos_normalizados = []

    for x, y, z in puntos:

        x_norm = x / max_distancia
        y_norm = y / max_distancia
        z_norm = z / max_distancia

        puntos_normalizados.append(
            (x_norm, y_norm, z_norm)
        )


    return puntos_normalizados


# --------------------------------------------------
# 6. Bucle de cámara
# --------------------------------------------------

while True:

    ret, frame = cap.read()

    if not ret:

        print("ERROR: No se pudo leer la cámara.")

        break


    frame = cv2.flip(frame, 1)


    # BGR -> RGB

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )


    # Crear imagen MediaPipe

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )


    # Timestamp

    frame_timestamp_ms += 33


    # Detectar

    result = detector.detect_for_video(
        mp_image,
        frame_timestamp_ms
    )


    # --------------------------------------------------
    # 7. Normalizar
    # --------------------------------------------------

    if result.hand_landmarks:

        for hand_index, hand_landmarks in enumerate(
            result.hand_landmarks
        ):

            puntos_normalizados = normalizar_landmarks(
                hand_landmarks
            )


            # Mostrar solamente una lectura por frame

            if frame_timestamp_ms != ultimo_timestamp:

                print()
                print("--------------------------------------")
                print(
                    f"MANO {hand_index + 1} - NORMALIZADA"
                )
                print("--------------------------------------")


                for index, (x, y, z) in enumerate(
                    puntos_normalizados
                ):

                    print(
                        f"Punto {index:02d}: "
                        f"x={x:.4f}, "
                        f"y={y:.4f}, "
                        f"z={z:.4f}"
                    )


                ultimo_timestamp = frame_timestamp_ms


            # ------------------------------------------
            # Dibujar landmarks
            # ------------------------------------------

            height, width, _ = frame.shape

            for landmark in hand_landmarks:

                x = int(landmark.x * width)
                y = int(landmark.y * height)

                cv2.circle(
                    frame,
                    (x, y),
                    5,
                    (0, 255, 0),
                    -1
                )


    # --------------------------------------------------
    # 8. Mostrar información
    # --------------------------------------------------

    cv2.putText(
        frame,
        "SignIA - Normalizacion",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )


    cv2.imshow(
        "SignIA - Normalizacion",
        frame
    )


    # ESC

    if cv2.waitKey(1) & 0xFF == 27:

        break


# --------------------------------------------------
# 9. Liberar recursos
# --------------------------------------------------

cap.release()

cv2.destroyAllWindows()

detector.close()


print()
print("======================================")
print("Normalizacion finalizada.")
print("======================================")