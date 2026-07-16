# Superset Setup — AtmoSync Dashboard

The Superset container is already defined in `docker-compose.yml`. This guide
gets you from "container running" to "live arbitrage dashboard" in ~15 minutes.

## 1. Start Superset

```bash
docker compose up -d zookeeper kafka superset
```

First boot runs `superset db upgrade`, creates an `admin/admin` user, and
starts on http://localhost:8088. Give it 1-2 minutes the first time.

## 2. Connect the database

Superset → Settings → Database Connections → + Database → SQLite.

The compose file mounts the project root to `/app` inside the container, so
the SQLAlchemy URI is:

```
sqlite:////app/atmosync.db
```

(four slashes: `sqlite://` + absolute path `/app/atmosync.db`)

Test the connection, then save it as `AtmoSync`.

> IMPORTANT: run `dbt run --profiles-dir .` from `dbt_atmosync/` (see project
> README) BEFORE connecting Superset, so the `spoilage_degradation` and
> `spoilage_arbitrage` tables already exist for it to find.

## 3. Add datasets

Settings → Datasets → + Dataset, schema `main`, and add these tables/views
directly (no SQL needed, dbt already built them):

- `spoilage_arbitrage` — the main dashboard table
- `spoilage_degradation` — for trend charts
- `sensor_data` — for raw/live monitoring

## 4. Build these charts

### A. "Reroute Alerts" (Table) — the headline widget
- Dataset: `spoilage_arbitrage`
- Columns: container_id, market_name, price_per_kg, net_arbitrage_value_per_kg, quality_tier
- Filter: `reroute_recommended = 1`
- Sort: net_arbitrage_value_per_kg, descending
- This is the direct answer to "which container should I reroute, and where."

### B. "Container Quality Status" (Big Number / Table)
- Dataset: `spoilage_degradation`
- Filter to latest reading per container (or just sort by event_timestamp desc, limit per container_id in SQL Lab if you want one row each — see `superset/queries.sql`)
- Color by quality_tier: GOOD=green, DEGRADING=amber, CRITICAL=red
- Use a conditional formatting rule on quality_remaining_pct

### C. "Spoilage Curve Over Time" (Line Chart)
- Dataset: `spoilage_degradation`
- X-axis: reading_seq (or event_timestamp)
- Y-axis: quality_remaining_pct
- Group by: container_id (one line per container)

### D. "Live Sensor Feed" (Table, auto-refresh)
- Dataset: `sensor_data`
- Columns: container_id, temperature, humidity, vibration, door_status, spoilage_risk, timestamp
- Sort: timestamp desc, limit 25
- Set chart auto-refresh interval to 5-10s for a "real-time" feel during a demo

### E. "Container Locations" (Map, optional)
- Dataset: `sensor_data`
- Needs latitude/longitude — use deck.gl Scatterplot chart type

## 5. Assemble the dashboard

New Dashboard → "AtmoSync — Spoilage Arbitrage Control Tower" → drag in
charts A-D (E optional). Put A (Reroute Alerts) at the top — it's the
money shot for your demo, matching the original use case: detect drift →
calculate arbitrage → alert trader to reroute.

## 6. For your presentation/demo

Run the simulator + consumer for a minute to generate fresh data, re-run
`dbt run`, then hit refresh on the dashboard — this shows the full
pipeline live: Kafka → SQLite → dbt → Superset.

See `superset/queries.sql` for ad-hoc SQL Lab queries if you want a
"latest reading per container" virtual dataset instead of building it as a
dbt model.
