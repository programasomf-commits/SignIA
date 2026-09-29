import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


print("======================================")
print("       SIGNIA - EXTRACCION LANDMARKS")
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

print("Detector de manos listo.")


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

# Para no imprimir coordenadas en todos los frames
ultimo_frame_mostrado = -1


# --------------------------------------------------
# 5. Bucle de captura
# --------------------------------------------------

while True:

    ret, frame = cap.read()

    if not ret:

        print("ERROR: No se pudo leer la cámara.")

        break


    frame = cv2.flip(frame, 1)


    # Convertir BGR -> RGB

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


    # Detectar manos

    result = detector.detect_for_video(
        mp_image,
        frame_timestamp_ms
    )


    # --------------------------------------------------
    # 6. Extraer landmarks
    # --------------------------------------------------

    if result.hand_landmarks:

        for hand_index, hand_landmarks in enumerate(
            result.hand_landmarks
        ):

            # Mostrar información una sola vez
            # por frame procesado

            if frame_timestamp_ms != ultimo_frame_mostrado:

                print()
                print("--------------------------------------")
                print(
                    f"MANO DETECTADA: {hand_index + 1}"
                )
                print("--------------------------------------")


                for landmark_index, landmark in enumerate(
                    hand_landmarks
                ):

                    print(
                        f"Punto {landmark_index:02d}: "
                        f"x={landmark.x:.4f}, "
                        f"y={landmark.y:.4f}, "
                        f"z={landmark.z:.4f}"
                    )


                ultimo_frame_mostrado = frame_timestamp_ms


    # --------------------------------------------------
    # 7. Mostrar cámara
    # --------------------------------------------------

    cv2.putText(
        frame,
        "Extraccion de landmarks",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )


    cv2.imshow(
        "SignIA - Landmarks",
        frame
    )


    # ESC

    if cv2.waitKey(1) & 0xFF == 27:

        break


# --------------------------------------------------
# 8. Liberar recursos
# --------------------------------------------------

cap.release()

cv2.destroyAllWindows()

detector.close()


print()
print("======================================")
print("Extraccion finalizada.")
print("======================================")