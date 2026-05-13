import json
import time
import pandas as pd
from kafka import KafkaProducer

TOPIC     = 'happiness-predictions'
BROKER    = 'localhost:9092'
DELAY_SEC = 0.05


def build_producer():
    return KafkaProducer(
        bootstrap_servers=BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    )


def run_producer(unified_csv):
    df       = pd.read_csv(unified_csv)
    producer = build_producer()

    print(f"Enviando {len(df)} registros al topic '{TOPIC}'...")

    for i, row in df.iterrows():
        event = {
            'country':      row['country'],
            'region':       row['region'],
            'year':         int(row['year']),
            'gdp':          float(row['gdp']),
            'family':       float(row['family']),
            'health':       float(row['health']),
            'freedom':      float(row['freedom']),
            'generosity':   float(row['generosity']),
            'trust':        float(row['trust']),
            'actual_score': float(row['score']),
        }
        producer.send(TOPIC, value=event)
        print(f"  [{i+1}/{len(df)}] {event['country']} ({event['year']}) → enviado")
        time.sleep(DELAY_SEC)

    producer.flush()
    producer.close()
    print("Producer finalizado ✓")