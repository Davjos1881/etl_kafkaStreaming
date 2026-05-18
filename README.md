Workshop 3 — Streaming ETL con Apache Kafka y Machine Learning

Reporte Felicidad Mundiad (2015–2019)

Instalación y ejecución

1. Instalar dependencias

        pip install -r requirements.txt
   
2. Levantar Kafka
   
        docker-compose up -d

3. Crear el topico de Kafka

        docker exec -it kafka kafka-topics --create --topic happiness-predictions --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

4. Crear la base de datos
   
Ejecuta mysql_schema/happiness_db.sql en MySQL Workbench 

6. Configurar la conexión a la base de datos

En scripts/db.py, actualizar el string de conexión:

    DB_URL = "mysql+pymysql://tu_usuario:tu_password@localhost:3306/happiness_db"
    
8. Entrenar el modelo

Ejecuta notebooks/model_training.ipynb de principio a fin. Genera model.pkl y scaler.pkl en models/.

9. Correr el pipeline

python scripts/main.py

Dataset:

Los datos crudos consisten en 5 archivos CSV del World Happiness Report, uno por año (2015-2019), publicados por la Sustainable Development Solutions Network. 
Cada archivo rankea países según las respuestas a la pregunta de la escalera de Cantril: 
que tan satisfecho estas con tu vida.

Filas por año:

2015: 158

2016: 157

2017: 155

2018: 156

2019: 156

Interpretación de columnas:

year: año de la encuesta

country: país encuestado

region: región geográfica

rank: posición en el ranking mundial ese año

score: puntaje de felicidad (escala 0-10), variable target

gdp: contribución del PIB per cápita al score

family: contribución del soporte social al score

health: contribución de la esperanza de vida saludable al score

freedom: contribución de la libertad de decisión al score

generosity: contribución de la generosidad al score

trust: contribución de la percepción de ausencia de corrupción al score

Las columnas gdp, family, health, freedom, generosity y trust no son valores absolutos, representan cuanto contribuye cada factor al score final.

Limpieza de datos

Problemas encontrados en el EDA:

Nombres de columnas inconsistentes entre años: la misma variable tenia hasta 3 nombres distintos según el año. Se unificaron bajo un esquema estandar.

Columnas exclusivas sin equivalente: años como 2015 y 2016 incluían Standard Error y Confidence Intervals, 2017 incluía Whisker.high y Whisker.low. Al no tener equivalente en los demás años se eliminaron.

Columna Region ausente en 2017-2019: se resolvió haciendo un join con el mapeo pais-region extraído de 2015. Los países sin match se completaron manualmente con un diccionario de fallback basado en conocimiento geográfico.

Nombres de países inconsistentes: el mismo país aparecía con nombres distintos según el año. Se unificaron antes del join de regiones.

Un único valor nulo: United Arab Emirates en 2018 tenia NaN en trust. Se imputó con la media de esa columna para ese año.

Decisiones de limpieza:

unify_country_names se ejecuta antes de fill_regions para garantizar que los alias queden resueltos antes del join.

Las columnas sin equivalente entre años se eliminan.

La columna rank se conserva en el dataset unificado pero no se usa como variable del modelo porque es una variable derivada del puntaje.

Modelo de Machine Learning

Modelo seleccionado: Regresión Lineal, debido a su simplicidad e interpretabilidad.

Variables seleccionadas: gdp, family, health, freedom, generosity, trust

Variables descartadas:

rank: derivada directamente del score.

year: el modelo aprendió un coeficiente negativo para esta variable, indicando que capturaba un artefacto del dataset (años recientes incluyen más países en desarrollo, bajando el promedio global) en lugar de una relación causal real.

country y region: categóricas sin aporte causal directo al puntaje.

Todas las variables se escalaron con StandardScaler antes del entrenamiento. El scaler se guardó como scaler.pkl para ser reutilizado en el consumer y garantizar que los datos de producción se transformen de la misma forma que los de entrenamiento.

Resultados:

MAE: 0.4486

RMSE: 0.5843

R2: 0.7265

Un R2 de 0.73 indica que el modelo explica el 73% de la varianza del happiness score con solo 6 variables.

Pipeline de Streaming

Arquitectura:

happiness_unified.csv -> producer.py -> Kafka topic (happiness-predictions) -> consumer.py -> MySQL (happiness_db) -> Dashboard Power BI

Formato del evento Kafka:

{

"country": "Colombia",

"region": "Latin America and Caribbean",

"year": 2019,

"gdp": 0.91,

"family": 1.07,

"health": 0.63,

"freedom": 0.38,

"generosity": 0.17,

"trust": 0.05,

"actual_score": 6.19

}

Validación de eventos:

INVALID_SCHEMA: falta algún campo requerido. Se guarda en raw con ese status y se omite la predicción.

INVALID_VALUES: algún campo numérico es negativo o no numérico. Se guarda en raw con ese status y se omite la predicción.

PREDICTION_ERROR: falla en tiempo de ejecución del modelo. Se guarda en raw y se actualiza el status.

VALID: evento correcto. Se guarda en raw, se genera predicción y se inserta en fact.

Los eventos inválidos nunca crashean el pipeline, se registran y se continúa con el siguiente mensaje.

Modelo Dimensional

Tablas:
raw_happiness_events: almacena cada evento Kafka exactamente como llegó, con su status de procesamiento.

dim_country: dimensión de países con su región geográfica.

dim_date: dimensión de tiempo, guarda solo el id y año.

dim_raw_event: expone el status y timestamp para auditoría.

fact_predictions: tabla de hechos con el puntaje actual, el predicho y el error de predicción.

Granularidad: una fila por evento Kafka procesado, equivalente a una predicción de happiness score para un país en un año específico.

Decisiones de diseño:

dim_country incluye region para permitir análisis agrupados por zona geográfica.

dim_raw_event existe para facilitar auditoría sin consultar directamente la tabla raw.

El consumer usa get_or_create para poblar las dimensiones en tiempo real en lugar de cargarlas previamente, porque los países y años se conocen solo cuando llega el evento.

Cada evento Kafka se procesa dentro de una transacción independiente, garantizando que un fallo en un evento no afecte los demás.

Dashboard

Construido en Power BI conectado directamente a MySQL mediante ODBC. Consta de dos páginas.

Página 1

Evaluación del modelo:

Error promedio de predicción

Predicciones por país

Prediccion vs Puntaje Real

Promedio del error de la prediccion

Página 2

Análisis de felicidad mundial:

Ranking de regiones por felicidad promedio

Evolución de felicidad por región (2015-2019)

Top 10 países más felices

Top 10 países menos felices

