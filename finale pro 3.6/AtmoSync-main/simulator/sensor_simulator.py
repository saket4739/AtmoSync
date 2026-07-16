import json
import random
import time
from datetime import datetime
from kafka import KafkaProducer
from config.settings import (
    KAFKA_BOOTSTRAP_SERVER,
    KAFKA_TOPIC,
    SIMULATOR_DELAY
)

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

containers = [
    "CONT-101",
    "CONT-102",
    "CONT-103",
    "CONT-104",
    "CONT-105"
]

print("AtmoSync Sensor Simulator Started...\n")

while True:

    temperature = round(random.uniform(2, 10), 2)
    humidity = round(random.uniform(50, 90), 2)
    vibration = round(random.uniform(0, 5), 2)

    battery = random.randint(60, 100)

    latitude = round(random.uniform(18.90, 19.30), 6)
    longitude = round(random.uniform(72.70, 73.10), 6)

    door = random.choice(["OPEN", "CLOSED"])

    spoilage = "HIGH" if temperature > 8 else "LOW"

    data = {
        "container_id": random.choice(containers),
        "temperature": temperature,
        "humidity": humidity,
        "vibration": vibration,
        "battery": battery,
        "latitude": latitude,
        "longitude": longitude,
        "door_status": door,
        "spoilage_risk": spoilage,
        "timestamp": datetime.now().isoformat()
    }

    producer.send(KAFKA_TOPIC, value=data)
    producer.flush()

    print(data)
    

    time.sleep(SIMULATOR_DELAY)