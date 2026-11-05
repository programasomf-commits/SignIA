from pathlib import Path

import joblib
import numpy as np

from backend.app.services.features import normalizar_landmarks


BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "ml_models" / "modelo_lenguaje_senas.pkl"

_model = None


def cargar_modelo():
    """Carga el modelo entrenado una sola vez."""
    global _model

    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"No se encontró el modelo: {MODEL_PATH}"
            )

        _model = joblib.load(MODEL_PATH)

    return _model


def preparar_entrada(landmarks):
    """
    Convierte los 21 landmarks en un vector de 63 características.

    vision_service entrega puntos normalizados como diccionarios x, y, z.
    Si se reciben coordenadas numéricas sin normalizar, aplica la función
    normalizar_landmarks del proyecto.
    """
    if not landmarks or len(landmarks) != 21:
        raise ValueError("Se requieren exactamente 21 landmarks.")

    if isinstance(landmarks[0], dict):
        puntos = [
            [p["x"], p["y"], p["z"]]
            for p in landmarks
        ]
        vector = np.asarray(puntos, dtype=float).reshape(1, 63)
    else:
        vector = normalizar_landmarks(landmarks).reshape(1, 63)

    if not np.isfinite(vector).all():
        raise ValueError("Los landmarks contienen valores no válidos.")

    return vector


def predecir_sena(landmarks):
    """
    Recibe los 21 landmarks y devuelve la clase predicha
    junto con la confianza del modelo.
    """
    modelo = cargar_modelo()
    entrada = preparar_entrada(landmarks)

    prediccion = modelo.predict(entrada)[0]
    probabilidades = modelo.predict_proba(entrada)
    confianza = float(np.max(probabilidades))

    return str(prediccion), confianza
