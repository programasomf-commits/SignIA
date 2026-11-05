# SignIA - Etapa 3: estado y limitaciones del conjunto de datos

## 1. Estado actual del conjunto de datos

El archivo `data/labels/dataset_master.csv` contiene 102 registros:
- 51 asociados a la glosa HOLA.
- 51 asociados a la glosa BUENOS_DIAS.

Todos los registros están asociados al identificador anónimo P01. Por lo
tanto, existe una sola identidad de participante en el conjunto de datos.

El conjunto contiene muestras con diferentes estructuras. Entre ellas se
encuentran secuencias dinámicas de 30 fotogramas, con 21 landmarks por
fotograma y tres coordenadas por landmark (x, y, z). Por ejemplo,
`LSM-HOLA-001.json` presenta una estructura de 30 x 21 x 3 y registra
la normalización tomando como origen el landmark 0 (muñeca) y utilizando
la distancia euclidiana máxima como escala.

No todos los registros del CSV deben considerarse automáticamente aptos
para el entrenamiento estático. Es necesario respetar el formato esperado
por cada proceso de entrenamiento.

## 2. Estado de la captura y detección

La etapa de captura y detección inicial se considera completada como
prueba funcional del proyecto. Se utilizaron muestras asociadas a P01
para comprobar la extracción de landmarks y el funcionamiento de la
comunicación entre el frontend y el backend.

La validación desde la interfaz permitió identificar la seña HOLA con
una confianza del 90 %, con respuesta HTTP 200 del servicio de predicción.
Esta prueba demuestra el funcionamiento del flujo en las condiciones
evaluadas, pero no constituye una evaluación de generalización entre
participantes.

La captura de muestras adicionales queda detenida temporalmente para
continuar con las demás actividades de preparación del proyecto.

## 3. Limitación de participantes

Actualmente, el conjunto de datos contiene un solo participante
identificado como P01. No se dispone de tres participantes reales
distintos para realizar una evaluación independiente por persona.

No se crearán identidades ficticias ni se atribuirán muestras de una
misma persona a participantes diferentes.

## 4. Consecuencias para la evaluación del modelo

La evaluación Leave-One-Group-Out propuesta para medir el desempeño
con participantes no vistos requiere grupos de participantes reales
suficientes. El script `backend/scripts/train_real.py` establece un
mínimo de tres participantes antes de realizar ese procedimiento.

Con los datos actuales no es posible ejecutar válidamente esa evaluación.
Por ello, no se afirma que el modelo haya demostrado generalización a
personas distintas de P01.

El clasificador funcional actual utiliza 63 características derivadas
de los 21 landmarks tridimensionales de una mano. Su funcionamiento
se ha comprobado mediante pruebas de integración, pero sus resultados
deben interpretarse como una validación funcional inicial.

## 5. Entrenamiento experimental

El proyecto conserva scripts de entrenamiento con objetivos y formatos
diferentes:

- `backend/scripts/train_experimental.py`: entrenamiento experimental
  con muestras estáticas asociadas a P01.
- `backend/scripts/train_real.py`: entrenamiento y evaluación agrupados
  por participante, sujeto a la disponibilidad de participantes reales.
- `backend/train_model.py`: entrenamiento experimental de secuencias
  dinámicas con forma de entrada de 30 x 21 x 3.

Estos procesos no son intercambiables. El modelo de secuencias dinámicas
no sustituye al clasificador estático utilizado actualmente por la API.

No se considera completada una evaluación Leave-One-Group-Out ni se
presentan resultados experimentales como prueba de generalización.

## 6. Trabajo pendiente

1. Mantener protegidos los datos originales y los archivos sensibles.
2. Continuar con la preparación técnica de SignIA para su despliegue.
3. Incorporar participantes adicionales cuando estén disponibles.
4. Verificar la calidad y compatibilidad de las muestras antes de
   utilizarlas en un entrenamiento.
5. Ejecutar la evaluación Leave-One-Group-Out cuando existan al menos
   tres participantes reales con datos adecuados.

## 7. Integridad y trazabilidad de los datos

Las muestras deben conservar su identificador real de participante.
No deben eliminarse ni modificarse los datos originales sin respaldo.

Los registros dinámicos y las muestras estáticas deben mantenerse
diferenciados de acuerdo con su estructura y finalidad.

La documentación de estas limitaciones permite presentar los resultados
de SignIA de manera transparente y evita atribuir al sistema capacidades
de reconocimiento que todavía no han sido evaluadas.
