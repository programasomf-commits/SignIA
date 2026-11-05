# Evaluación experimental del clasificador SignIA con muestras P01

**Fecha:** 5 de noviembre de 2026  
**Proyecto:** SignIA – Interpretación de Lengua de Señas Mexicana (LSM)

## 1. Objetivo

Evaluar experimentalmente un clasificador Random Forest para distinguir las glosas HOLA y BUENOS_DIAS mediante características normalizadas de los landmarks de la mano.

## 2. Datos utilizados

Los datos proceden de `data/labels/dataset_master.csv` y de los archivos JSON asociados.

Se utilizaron exclusivamente muestras estáticas de la persona identificada como P01.

| Glosa | Muestras válidas |
|---|---:|
| HOLA | 20 |
| BUENOS_DIAS | 21 |
| **Total** | **41** |

Se omitieron 61 registros que no cumplían los criterios de lectura y validación del entrenador experimental. Entre ellos se encuentran registros secuenciales y un registro sin landmarks válidos.

Cada muestra utilizada contiene 21 landmarks con tres coordenadas por punto. Después de la normalización se obtiene un vector de 63 características.

## 3. Configuración experimental

Se utilizó un clasificador `RandomForestClassifier` con los siguientes parámetros:

- Número de árboles: 200.
- Semilla aleatoria: 42.
- Balanceo de clases: `class_weight="balanced"`.
- División de datos: 80 % para entrenamiento y 20 % para prueba.
- Estratificación: activada.
- Evaluación: `accuracy_score`, `classification_report` y `confusion_matrix`.

La evaluación se realizó mediante una instancia temporal del clasificador en memoria. No se guardó ni sobrescribió ningún modelo del proyecto.

## 4. Resultados

| Indicador | Resultado |
|---|---:|
| Muestras de entrenamiento | 32 |
| Muestras de prueba | 9 |
| Exactitud | 1.0000 (100 %) |
| Precisión macro | 1.00 |
| Recall macro | 1.00 |
| F1-score macro | 1.00 |
| F1-score ponderado | 1.00 |

### 4.1. Resultados por clase

| Clase | Precisión | Recall | F1-score | Soporte |
|---|---:|---:|---:|---:|
| BUENOS_DIAS | 1.00 | 1.00 | 1.00 | 5 |
| HOLA | 1.00 | 1.00 | 1.00 | 4 |

### 4.2. Matriz de confusión

Orden de clases: BUENOS_DIAS, HOLA.

| Clase real | Predicción BUENOS_DIAS | Predicción HOLA |
|---|---:|---:|
| BUENOS_DIAS | 5 | 0 |
| HOLA | 0 | 4 |

Las nueve muestras de prueba fueron clasificadas correctamente en esta ejecución.

## 5. Interpretación

Los resultados muestran que el clasificador experimental distinguió correctamente las dos glosas en las nueve muestras reservadas para prueba.

Sin embargo, el resultado debe interpretarse dentro de su alcance: todas las muestras pertenecen a P01 y el conjunto de prueba contiene únicamente nueve registros. Por tanto, el resultado no demuestra que el clasificador generalice a personas diferentes ni representa una medida definitiva del rendimiento de SignIA en condiciones reales.

## 6. Limitaciones

- Las muestras evaluadas corresponden a una sola persona (P01).
- El conjunto de prueba es reducido.
- Los registros secuenciales no se utilizaron en esta evaluación estática.
- La evaluación no sustituye una validación con participantes independientes.
- Los resultados corresponden al clasificador experimental entrenado durante esta prueba en memoria; no deben atribuirse automáticamente al modelo activo utilizado por la página web.

## 7. Conclusión

Se realizó una evaluación experimental reproducible del procedimiento de clasificación estática de SignIA para las glosas HOLA y BUENOS_DIAS. Con 41 muestras válidas de P01, la división estratificada produjo 32 muestras de entrenamiento y nueve de prueba, obteniendo una exactitud de 100 % en esta ejecución.

Los resultados constituyen una evidencia inicial del funcionamiento del clasificador con las muestras disponibles. No obstante, se reconoce que todavía no permiten afirmar una capacidad de generalización a otros participantes.

**Integridad del proyecto:** esta evaluación se ejecutó en memoria y no modificó el modelo activo ni los archivos de modelos existentes.
