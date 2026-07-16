"""
Creates the AtmoSync SQLite database with the full sensor_data schema.
NOTE: This was previously out of sync with reset_database.py (missing
battery/latitude/longitude/door_status/spoilage_risk columns). Fixed to
match the live schema used by streaming/consumer.py.
"""
import sqlite3
from config.settings import DATABASE_NAME

conn = sqlite3.connect(DATABASE_NAME)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS sensor_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    container_id TEXT,
    temperature REAL,
    humidity REAL,
    vibration REAL,
    battery INTEGER,
    latitude REAL,
    longitude REAL,
    door_status TEXT,
    spoilage_risk TEXT,
    timestamp TEXT
)
""")

conn.commit()
conn.close()
print("Database created successfully!")
