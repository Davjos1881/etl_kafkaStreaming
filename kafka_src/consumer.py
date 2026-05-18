import json
import pickle
import numpy as np
from kafka import KafkaConsumer
from scripts.db import (get_engine, get_or_create_country, get_or_create_date,
                insert_raw_event, insert_dim_raw_event, insert_prediction,
                REQUIRED_FIELDS, NUMERIC_FIELDS, FEATURES)

TOPIC    = 'happiness-predictions'
BROKER   = 'localhost:9092'
GROUP_ID = 'happiness-consumer-group'


def load_model(model_path, scaler_path):
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    with open(scaler_path, 'rb') as f:
        scaler = pickle.load(f)
    return model, scaler


def validate_schema(event):
    missing = [f for f in REQUIRED_FIELDS if f not in event]
    if missing:
        return False, 'INVALID_SCHEMA'
    return True, 'VALID'


def validate_values(event):
    for field in NUMERIC_FIELDS:
        val = event.get(field)
        if val is None or not isinstance(val, (int, float)):
            return False, 'INVALID_VALUES'
        if val < 0:
            return False, 'INVALID_VALUES'
    return True, 'VALID'


def predict(event, model, scaler):
    features = np.array([[event[f] for f in FEATURES]])
    scaled   = scaler.transform(features)
    return float(model.predict(scaled)[0])


def process_event(event, model, scaler, conn):
    from sqlalchemy import text

    #Guardar raw antes de validacion
    raw_id = insert_raw_event(conn, event, status='VALID')

    #Validar schema
    ok, status = validate_schema(event)
    if not ok:
        conn.execute(text("UPDATE raw_happiness_events SET status = :s WHERE id = :id"),
                     {"s": status, "id": raw_id})
        insert_dim_raw_event(conn, raw_id, status)
        print(f"{event.get('country', '?')} -> {status}")
        return

    #Validar valores
    ok, status = validate_values(event)
    if not ok:
        conn.execute(text("UPDATE raw_happiness_events SET status = :s WHERE id = :id"),
                     {"s": status, "id": raw_id})
        insert_dim_raw_event(conn, raw_id, status)
        print(f"{event.get('country', '?')} -> {status}")
        return

    #Dimensiones
    insert_dim_raw_event(conn, raw_id, 'VALID')
    country_id = get_or_create_country(conn, event['country'], event['region'])
    date_id    = get_or_create_date(conn, event['year'])

    #Predecir
    try:
        predicted = predict(event, model, scaler)
        insert_prediction(conn, raw_id, country_id, date_id, predicted, event['actual_score'])
        print(f"{event['country']} ({event['year']}) -> predicted: {predicted:.4f} | actual: {event['actual_score']:.4f}")
    except Exception as e:
        conn.execute(text("UPDATE raw_happiness_events SET status = :s WHERE id = :id"),
                     {"s": "PREDICTION_ERROR", "id": raw_id})
        print(f"{event['country']} -> PREDICTION_ERROR: {e}")


def run_consumer(model_path, scaler_path):
    model, scaler = load_model(model_path, scaler_path)
    engine = get_engine()

    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=BROKER,
        group_id=GROUP_ID,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
    )

    print(f"Escuchando topic '{TOPIC}'...")

    try:
        for message in consumer:
            event = message.value
            with engine.begin() as conn:
                process_event(event, model, scaler, conn)
    except KeyboardInterrupt:
        print("\nConsumer detenido manualmente.")
    finally:
        consumer.close()
        print("Consumer finalizado")