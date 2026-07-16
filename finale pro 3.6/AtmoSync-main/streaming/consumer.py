from kafka import KafkaConsumer
import json
import sqlite3

from scripts.validator import validate_sensor_data
from config.settings import (
    KAFKA_BOOTSTRAP_SERVER,
    KAFKA_TOPIC,
    DATABASE_NAME
)
# Connect to SQLite
conn = sqlite3.connect(DATABASE_NAME)
cursor = conn.cursor()

# Connect to Kafka
consumer = KafkaConsumer(
    "sensor-data",
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVER,
    auto_offset_reset="latest",
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)

print("Waiting for sensor data...\n")

for message in consumer:
    data = message.value

    if not validate_sensor_data(data):
        print("Invalid data skipped:", data)
        continue

    cursor.execute("""
        INSERT INTO sensor_data (
            container_id,
            temperature,
            humidity,
            vibration,
            battery,
            latitude,
            longitude,
            door_status,
            spoilage_risk,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["container_id"],
        data["temperature"],
        data["humidity"],
        data["vibration"],
        data["battery"],
        data["latitude"],
        data["longitude"],
        data["door_status"],
        data["spoilage_risk"],
        data["timestamp"]
    ))

    conn.commit()

    print("Saved:", data)
    

conn.close()