from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.app.core.config import UMBRAL_CONFIANZA
from backend.app.db.database import get_db
from backend.app.models.registro_prediccion import RegistroPrediccion
from backend.app.services.ml_service import predecir_sena
from backend.app.services.vision_service import procesar_imagen


router = APIRouter(
    prefix="/api/v1",
    tags=["prediction"]
)


@router.post("/predict")
async def predict(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Recibe una imagen, detecta landmarks, clasifica la seña
    y registra las predicciones que superan el umbral de confianza.
    """

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser una imagen."
        )

    image_bytes = await file.read()

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="La imagen esta vacia."
        )

    try:
        vision_result = procesar_imagen(image_bytes)

    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if not vision_result.get("hand_detected", False):
        raise HTTPException(
            status_code=400,
            detail="No se detecto una mano en la imagen."
        )

    landmarks = vision_result.get("landmarks", [])

    try:
        glosa, confianza = predecir_sena(landmarks)

    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error al ejecutar el modelo de clasificacion: {exc}"
        )

    if confianza < UMBRAL_CONFIANZA:
        return {
            "status": "low_confidence",
            "prediction": None,
            "confidence": confianza,
            "threshold": UMBRAL_CONFIANZA,
            "message": "La confianza no alcanza el umbral requerido. No se registro la prediccion.",
            "vision": vision_result
        }

    registro = RegistroPrediccion(
        glosa_predicha=glosa,
        confianza=confianza
    )

    try:
        db.add(registro)
        db.commit()
        db.refresh(registro)

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"No fue posible guardar la prediccion: {exc}"
        )

    return {
        "status": "success",
        "prediction": glosa,
        "confidence": confianza,
        "registro_id": registro.id,
        "landmarks_count": len(landmarks),
        "vision": vision_result
    }
