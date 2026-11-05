
import json
from collections import Counter
from pathlib import Path


DATASET_DIR = Path("data/raw")
FRAMES_ESPERADOS = 30
LANDMARKS_ESPERADOS = 21
COORDENADAS_ESPERADAS = 3


def validar_muestra(archivo):
    errores = []

    try:
        with archivo.open("r", encoding="utf-8") as file:
            datos = json.load(file)
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"No se pudo leer el JSON: {exc}"]

    if not isinstance(datos, dict):
        return None, ["La raíz del JSON debe ser un objeto."]

    sample_id = datos.get("sample_id")
    label = datos.get("label")
    sequence = datos.get("sequence")

    if not isinstance(sample_id, str) or not sample_id.strip():
        errores.append("Falta un sample_id válido.")

    if not isinstance(label, str) or not label.strip():
        errores.append("Falta una etiqueta válida.")

    if datos.get("language") != "LSM":
        errores.append("El campo language debe ser LSM.")

    if not isinstance(sequence, list):
        errores.append("El campo sequence debe ser una lista.")
        return datos, errores

    if len(sequence) != FRAMES_ESPERADOS:
        errores.append(
            f"Se esperaban {FRAMES_ESPERADOS} frames; "
            f"se encontraron {len(sequence)}."
        )

    for i, frame in enumerate(sequence):
        if not isinstance(frame, list):
            errores.append(f"El frame {i + 1} no es una lista.")
            continue

        if len(frame) != LANDMARKS_ESPERADOS:
            errores.append(
                f"El frame {i + 1} tiene {len(frame)} landmarks; "
                f"se esperaban {LANDMARKS_ESPERADOS}."
            )
            continue

        for j, landmark in enumerate(frame):
            if not isinstance(landmark, (list, tuple)):
                errores.append(
                    f"Landmark {j + 1} del frame {i + 1} "
                    "no es una lista o tupla."
                )
                continue

            if len(landmark) != COORDENADAS_ESPERADAS:
                errores.append(
                    f"Landmark {j + 1} del frame {i + 1} "
                    "no tiene 3 coordenadas."
                )
                continue

            for coordenada in landmark:
                if (
                    isinstance(coordenada, bool)
                    or not isinstance(coordenada, (int, float))
                ):
                    errores.append(
                        f"Coordenada no numérica en el frame {i + 1}, "
                        f"landmark {j + 1}."
                    )
                    break

    if datos.get("frames") != len(sequence):
        errores.append("El metadato frames no coincide con sequence.")

    if datos.get("landmarks_per_frame") != LANDMARKS_ESPERADOS:
        errores.append("landmarks_per_frame debe ser 21.")

    if datos.get("coordinates_per_landmark") != COORDENADAS_ESPERADAS:
        errores.append("coordinates_per_landmark debe ser 3.")

    if datos.get("shape") != [
        len(sequence),
        LANDMARKS_ESPERADOS,
        COORDENADAS_ESPERADAS,
    ]:
        errores.append("El campo shape no coincide con la estructura.")

    return datos, errores


def main():
    print("=" * 46)
    print("     SIGNIA - VALIDACION GENERAL DATASET")
    print("=" * 46)

    if not DATASET_DIR.exists():
        print(f"ERROR: No existe la carpeta {DATASET_DIR}")
        return 1

    archivos = sorted(DATASET_DIR.glob("LSM-*.json"))

    if not archivos:
        print(f"No se encontraron archivos LSM-*.json en {DATASET_DIR}")
        return 1

    etiquetas = Counter()
    identificadores = {}
    muestras_correctas = 0
    muestras_con_errores = 0

    for archivo in archivos:
        print(f"\nArchivo: {archivo}")

        datos, errores = validar_muestra(archivo)

        if datos is not None:
            label = datos.get("label")
            sample_id = datos.get("sample_id")

            if isinstance(label, str) and label.strip():
                etiquetas[label.strip().upper()] += 1

            if isinstance(sample_id, str) and sample_id.strip():
                if sample_id in identificadores:
                    errores.append(
                        "sample_id duplicado; también aparece en "
                        f"{identificadores[sample_id]}."
                    )
                else:
                    identificadores[sample_id] = archivo

            if sample_id != archivo.stem:
                errores.append(
                    "El sample_id no coincide con el nombre del archivo."
                )

        if errores:
            muestras_con_errores += 1
            print("  RESULTADO: CON ERRORES")
            for error in errores:
                print(f"  - {error}")
        else:
            muestras_correctas += 1
            print("  RESULTADO: VALIDADA")

    print("\n" + "=" * 46)
    print("RESUMEN DEL DATASET")
    print("=" * 46)
    print(f"Archivos encontrados: {len(archivos)}")
    print(f"Muestras válidas: {muestras_correctas}")
    print(f"Muestras con errores: {muestras_con_errores}")

    print("\nMuestras por etiqueta:")
    for etiqueta, cantidad in sorted(etiquetas.items()):
        print(f"  {etiqueta}: {cantidad}")

    if muestras_con_errores:
        print("\nRESULTADO GENERAL: HAY MUESTRAS QUE REVISAR.")
        return 1

    print("\nRESULTADO GENERAL: TODAS LAS MUESTRAS SON VÁLIDAS.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
