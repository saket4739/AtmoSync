import sqlite3

conn = sqlite3.connect("atmosync.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS sensor_data")

cursor.execute("""
CREATE TABLE sensor_data(
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

print("Database Reset Successfully")