import math
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


MODEL_PATH = Path("models/hand_landmarker.task")


def normalizar_landmarks(hand_landmarks):
    """
    Normaliza los 21 landmarks tomando la muneca
    (landmark 0) como origen y utilizando la distancia
    euclidiana maxima como escala.
    """

    wrist = hand_landmarks[0]

    puntos = []

    for landmark in hand_landmarks:
        x = landmark.x - wrist.x
        y = landmark.y - wrist.y
        z = landmark.z - wrist.z

        puntos.append((x, y, z))

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

    return [
        (
            x / max_distancia,
            y / max_distancia,
            z / max_distancia
        )
        for x, y, z in puntos
    ]


def crear_detector():
    """
    Crea el detector de manos de MediaPipe.
    """

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"No se encontro el modelo: {MODEL_PATH}"
        )

    base_options = python.BaseOptions(
        model_asset_path=str(MODEL_PATH)
    )

    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.IMAGE,
        num_hands=1,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5
    )

    return vision.HandLandmarker.create_from_options(
        options
    )


def procesar_imagen(image_bytes: bytes):
    """
    Procesa una imagen recibida por la API y extrae
    los landmarks normalizados de la mano.
    """

    image_array = bytearray(image_bytes)

    image = cv2.imdecode(
        np.frombuffer(
            image_array,
            dtype=np.uint8
        ),
        cv2.IMREAD_COLOR
    )

    if image is None:
        raise ValueError(
            "No fue posible decodificar la imagen."
        )

    image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=image
    )

    detector = crear_detector()

    try:
        result = detector.detect(mp_image)
    finally:
        detector.close()

    if not result.hand_landmarks:
        return {
            "hand_detected": False,
            "landmarks": [],
            "landmarks_per_hand": 0,
            "coordinates_per_landmark": 3
        }

    hand_landmarks = result.hand_landmarks[0]

    puntos_normalizados = normalizar_landmarks(
        hand_landmarks
    )

    return {
        "hand_detected": True,
        "landmarks": [
            {
                "x": point[0],
                "y": point[1],
                "z": point[2]
            }
            for point in puntos_normalizados
        ],
        "landmarks_per_hand": len(
            puntos_normalizados
        ),
        "coordinates_per_landmark": 3
    }
