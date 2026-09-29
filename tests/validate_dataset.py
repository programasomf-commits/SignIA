import json
from pathlib import Path


print("======================================")
print("     SIGNIA - VALIDACION DATASET")
print("======================================")


# --------------------------------------------------
# Archivo a validar
# --------------------------------------------------

archivo = Path(
    "data/raw/LSM-HOLA-001.json"
)


# --------------------------------------------------
# Verificar existencia
# --------------------------------------------------

if not archivo.exists():

    print()
    print("ERROR: No existe el archivo:")
    print(archivo)

    exit()


print()
print("Archivo encontrado:")
print(archivo)


# --------------------------------------------------
# Leer JSON
# --------------------------------------------------

with open(
    archivo,
    "r",
    encoding="utf-8"
) as file:

    datos = json.load(file)


print()
print("JSON cargado correctamente.")


# --------------------------------------------------
# Datos principales
# --------------------------------------------------

sample_id = datos["sample_id"]

label = datos["label"]

language = datos["language"]

frames = datos["frames"]

landmarks = datos["landmarks_per_frame"]

coordinates = datos[
    "coordinates_per_landmark"
]

shape = datos["shape"]

sequence = datos["sequence"]


# --------------------------------------------------
# Mostrar información
# --------------------------------------------------

print()
print("--------------------------------------")
print("INFORMACION DE LA MUESTRA")
print("--------------------------------------")

print("Sample ID:", sample_id)

print("Etiqueta:", label)

print("Lenguaje:", language)

print("Frames:", frames)

print("Landmarks por frame:", landmarks)

print("Coordenadas:", coordinates)

print("Shape:", shape)


# --------------------------------------------------
# Validaciones
# --------------------------------------------------

print()
print("--------------------------------------")
print("VALIDACIONES")
print("--------------------------------------")


# Validación 1

if len(sequence) == 30:

    print("OK - 30 frames encontrados.")

else:

    print(
        "ERROR - Frames encontrados:",
        len(sequence)
    )


# Validación 2

if all(
    len(frame) == 21
    for frame in sequence
):

    print(
        "OK - Cada frame tiene 21 landmarks."
    )

else:

    print(
        "ERROR - Algunos frames no tienen 21 landmarks."
    )


# Validación 3

coordenadas_correctas = True

for frame in sequence:

    for landmark in frame:

        if len(landmark) != 3:

            coordenadas_correctas = False


if coordenadas_correctas:

    print(
        "OK - Cada landmark tiene X, Y, Z."
    )

else:

    print(
        "ERROR - Hay landmarks sin 3 coordenadas."
    )


# --------------------------------------------------
# Cantidad total de valores
# --------------------------------------------------

total_valores = (
    frames *
    landmarks *
    coordinates
)


print()
print("--------------------------------------")
print("CALCULO DE DATOS")
print("--------------------------------------")

print(
    f"{frames} frames × "
    f"{landmarks} landmarks × "
    f"{coordinates} coordenadas"
)

print(
    "Total de valores:",
    total_valores
)


# --------------------------------------------------
# Resultado
# --------------------------------------------------

if (
    len(sequence) == 30
    and all(
        len(frame) == 21
        for frame in sequence
    )
    and coordenadas_correctas
):

    print()
    print("======================================")
    print("     DATASET VALIDADO CORRECTAMENTE")
    print("======================================")

else:

    print()
    print("======================================")
    print("       DATASET CON ERRORES")
    print("======================================")