import pandas as pd
from kafka import KafkaProducer
import json
import time
import random

KAFKA_BROKER_URL = 'localhost:9092'
TOPIC_NAME = 'retail_events_topic'
DATA_FILE_PATH = '../data/raw/events.csv'
# Jika ingin cepat, komentari atau kecilkan nilai sleep time ini
# SLEEP_TIME_MIN = 0.001 
# SLEEP_TIME_MAX = 0.005 

print(f"Producer: Starting for topic '{TOPIC_NAME}'...")
try:
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER_URL,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    print("Producer: Connected to Kafka.")
except Exception as e:
    print(f"Producer: Kafka connection error: {e}")
    exit()

try:
    df = pd.read_csv(DATA_FILE_PATH)
    print(f"Producer: Read {len(df)} rows from {DATA_FILE_PATH}.")
    
    count = 0
    total_rows = len(df)
    for index, row in df.iterrows():
        message = row.to_dict()
        producer.send(TOPIC_NAME, value=message)
        count += 1
        if count % 10000 == 0 or count == total_rows:
             print(f"Producer: Sent {count}/{total_rows} messages...")
        # Hapus atau kecilkan sleep untuk pengiriman lebih cepat
        # time.sleep(random.uniform(SLEEP_TIME_MIN, SLEEP_TIME_MAX)) 
    
    print(f"Producer: All {count} messages sent to topic '{TOPIC_NAME}'.")

except FileNotFoundError:
    print(f"Producer: Error - File not found at {DATA_FILE_PATH}")
except Exception as e:
    print(f"Producer: Error during message sending: {e}")
finally:
    if 'producer' in locals() and producer:
        print("Producer: Closing Kafka Producer...")
        producer.flush()
        producer.close()
        print("Producer: Closed.")