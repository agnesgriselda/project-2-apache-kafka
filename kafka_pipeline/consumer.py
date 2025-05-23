from kafka import KafkaConsumer
import json
import pandas as pd
import os

KAFKA_BROKER_URL = 'localhost:9092'
TOPIC_NAME = 'retail_events_topic'
GROUP_ID = 'retail_event_consumer_group_2' # PENTING: Jika ingin reset total dari awal topic, ganti GROUP_ID ini
BATCH_OUTPUT_DIR = '../data/processed_batches/'
BATCH_SIZE = 10000

if not os.path.exists(BATCH_OUTPUT_DIR):
    os.makedirs(BATCH_OUTPUT_DIR)
    print(f"Consumer: Created directory '{BATCH_OUTPUT_DIR}'.")

print(f"Consumer: Starting for topic '{TOPIC_NAME}', group '{GROUP_ID}'...")
try:
    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=KAFKA_BROKER_URL,
        auto_offset_reset='earliest', # Hanya berlaku jika GROUP_ID baru atau offset hilang
        enable_auto_commit=True,      # Offset akan di-commit otomatis
        group_id=GROUP_ID,
        consumer_timeout_ms=30000,  # Timeout 30 detik (30000 ms), bisa disesuaikan
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )
    print("Consumer: Connected to Kafka.")
except Exception as e:
    print(f"Consumer: Kafka connection error: {e}")
    exit()

batch_messages = []
batch_file_count = 0
messages_processed_total = 0

try:
    print("Consumer: Waiting for messages...")
    for message in consumer: # Loop ini akan berhenti jika consumer_timeout_ms tercapai
        batch_messages.append(message.value)
        messages_processed_total +=1

        if messages_processed_total % 1000 == 0:
            print(f"Consumer: Total messages received: {messages_processed_total}, current batch size: {len(batch_messages)}")

        if len(batch_messages) >= BATCH_SIZE:
            batch_file_count += 1
            file_name = os.path.join(BATCH_OUTPUT_DIR, f'batch_{batch_file_count:03d}.csv')
            
            df_batch = pd.DataFrame(batch_messages)
            df_batch.to_csv(file_name, index=False)
            
            print(f"Consumer: Batch {batch_file_count} ({len(batch_messages)} messages) saved to: {file_name}")
            batch_messages = []
    
    # Pesan ini akan muncul jika loop for selesai (karena timeout atau tidak ada pesan lagi)
    print(f"Consumer: Finished processing messages or timeout reached. Total messages processed: {messages_processed_total}")

except KeyboardInterrupt:
    print("Consumer: Interrupted by user (Ctrl+C).")
except Exception as e:
    print(f"Consumer: Error during message processing: {e}")
finally:
    if batch_messages: 
        batch_file_count += 1
        file_name = os.path.join(BATCH_OUTPUT_DIR, f'batch_{batch_file_count:03d}_final.csv')
        df_batch = pd.DataFrame(batch_messages)
        df_batch.to_csv(file_name, index=False)
        print(f"Consumer: Final batch ({len(batch_messages)} messages) saved to: {file_name}")

    if 'consumer' in locals() and consumer:
        print("Consumer: Closing Kafka Consumer...")
        consumer.close()
        print("Consumer: Closed.")