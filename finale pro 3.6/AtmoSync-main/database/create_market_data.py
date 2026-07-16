"""
Creates and seeds reference tables that AtmoSync's arbitrage logic depends on:
  - markets: candidate delivery markets a container could be rerouted to
  - commodity_prices: per-commodity, per-market price snapshots (mocked,
    standing in for a live pricing feed / Snowflake external table)

These are static reference data (slowly changing), separate from the
high-frequency sensor_data stream, which is why they live in their own
seed step rather than being produced by the Kafka simulator.
"""
import sqlite3
from config.settings import DATABASE_NAME

# Mumbai-region markets, matching the lat/long range the simulator uses
MARKETS = [
    ("MKT-PRIMARY", "Vashi APMC Market", 19.0770, 73.0000),
    ("MKT-SEC-01", "Kalyan Wholesale Market", 19.2403, 73.1305),
    ("MKT-SEC-02", "Panvel Agri Hub", 18.9894, 73.1175),
    ("MKT-SEC-03", "Thane Fresh Produce Market", 19.2183, 72.9781),
]

# Avocado price (INR/kg) at each market, with secondary markets priced at a
# premium to simulate the "reroute for a better price" arbitrage scenario.
COMMODITY_PRICES = [
    ("AVOCADO", "MKT-PRIMARY", 210.00),
    ("AVOCADO", "MKT-SEC-01", 245.00),
    ("AVOCADO", "MKT-SEC-02", 232.00),
    ("AVOCADO", "MKT-SEC-03", 198.00),
]

conn = sqlite3.connect(DATABASE_NAME)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS markets (
    market_id TEXT PRIMARY KEY,
    market_name TEXT,
    latitude REAL,
    longitude REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS commodity_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    commodity TEXT,
    market_id TEXT,
    price_per_kg REAL,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (market_id) REFERENCES markets(market_id)
)
""")

cursor.executemany(
    "INSERT OR REPLACE INTO markets (market_id, market_name, latitude, longitude) VALUES (?, ?, ?, ?)",
    MARKETS,
)
cursor.executemany(
    "INSERT INTO commodity_prices (commodity, market_id, price_per_kg) VALUES (?, ?, ?)",
    COMMODITY_PRICES,
)

conn.commit()
conn.close()
print(f"Seeded {len(MARKETS)} markets and {len(COMMODITY_PRICES)} commodity prices.")
