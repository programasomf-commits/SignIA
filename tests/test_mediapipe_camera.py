import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


print("======================================")
print("        SIGNIA - PRUEBA DE MANOS")
print("======================================")

print("OpenCV:", cv2.__version__)
print("MediaPipe:", mp.__version__)


# --------------------------------------------------
# 1. Ruta del modelo
# --------------------------------------------------

MODEL_PATH = "models/hand_landmarker.task"


# --------------------------------------------------
# 2. Configuración del detector
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

print("Cargando modelo de MediaPipe...")

detector = vision.HandLandmarker.create_from_options(options)

print("Modelo cargado correctamente.")


# --------------------------------------------------
# 4. Abrir cámara
# --------------------------------------------------

cap = cv2.VideoCapture(0)

if not cap.isOpened():

    print("ERROR: No se pudo abrir la cámara.")

    detector.close()

    exit()


print("Cámara iniciada correctamente.")
print("Coloca tus manos frente a la cámara.")
print("Presiona ESC para salir.")


# --------------------------------------------------
# 5. Contador de frames
# --------------------------------------------------

frame_timestamp_ms = 0


# --------------------------------------------------
# 6. Bucle principal
# --------------------------------------------------

while True:

    ret, frame = cap.read()

    if not ret:

        print("ERROR: No se pudo leer la cámara.")

        break


    # Efecto espejo
    frame = cv2.flip(frame, 1)


    # OpenCV utiliza BGR
    # MediaPipe necesita RGB

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )


    # Convertir imagen para MediaPipe

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )


    # Incrementar timestamp

    frame_timestamp_ms += 33


    # Procesar frame

    result = detector.detect_for_video(
        mp_image,
        frame_timestamp_ms
    )


    # --------------------------------------------------
    # 7. Dibujar landmarks
    # --------------------------------------------------

    if result.hand_landmarks:

        for hand_index, hand_landmarks in enumerate(
            result.hand_landmarks
        ):

            # Dibujar puntos

            for landmark in hand_landmarks:

                height, width, _ = frame.shape

                x = int(landmark.x * width)

                y = int(landmark.y * height)

                cv2.circle(
                    frame,
                    (x, y),
                    5,
                    (0, 255, 0),
                    -1
                )


            # Dibujar conexiones

            connections = [
                (0, 1),
                (1, 2),
                (2, 3),
                (3, 4),

                (0, 5),
                (5, 6),
                (6, 7),
                (7, 8),

                (0, 9),
                (9, 10),
                (10, 11),
                (11, 12),

                (0, 13),
                (13, 14),
                (14, 15),
                (15, 16),

                (0, 17),
                (17, 18),
                (18, 19),
                (19, 20),

                (5, 9),
                (9, 13),
                (13, 17),

                (0, 17)
            ]


            for start, end in connections:

                height, width, _ = frame.shape

                x1 = int(
                    hand_landmarks[start].x * width
                )

                y1 = int(
                    hand_landmarks[start].y * height
                )

                x2 = int(
                    hand_landmarks[end].x * width
                )

                y2 = int(
                    hand_landmarks[end].y * height
                )


                cv2.line(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )


    # --------------------------------------------------
    # 8. Mostrar información
    # --------------------------------------------------

    hands_detected = len(result.hand_landmarks)

    cv2.putText(
        frame,
        f"Manos detectadas: {hands_detected}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )


    # Mostrar ventana

    cv2.imshow(
        "SignIA - Hand Landmarker",
        frame
    )


    # ESC para salir

    if cv2.waitKey(1) & 0xFF == 27:

        break


# --------------------------------------------------
# 9. Liberar recursos
# --------------------------------------------------

cap.release()

cv2.destroyAllWindows()

detector.close()


print("======================================")
print("Prueba finalizada.")
print("======================================")