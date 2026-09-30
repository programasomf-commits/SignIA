from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.app.services.vision_service import procesar_imagen


router = APIRouter(
    prefix="/api/v1",
    tags=["prediction"]
)


@router.post("/predict")
async def predict(file: UploadFile = File(...)):
    """
    Recibe una imagen y procesa los landmarks
    de la mano mediante MediaPipe.
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
        result = procesar_imagen(image_bytes)

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    return {
        "status": "ok",
        "prediction": None,
        "vision": result
    }