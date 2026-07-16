import sqlite3

conn = sqlite3.connect("atmosync.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM sensor_data")

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
