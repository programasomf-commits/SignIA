import numpy as np


def normalizar_landmarks(landmarks):
    """Hace el vector invariante a posición y escala de la mano.
    Resta la muñeca (landmark 0) y divide entre la mayor distancia a ella.
    """
    puntos = np.array(landmarks, dtype=float).reshape(21, 3)
    puntos = puntos - puntos[0]
    escala = np.max(np.linalg.norm(puntos, axis=1))

    if escala > 0:
        puntos = puntos / escala

    return puntos.flatten()
