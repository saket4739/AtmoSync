-- Staging layer: light cleaning/typing over the raw Kafka -> SQLite stream.
-- No business logic here, just standardize types and drop obviously
-- malformed rows that slipped past scripts/validator.py historically.

select
    id,
    container_id,
    cast(temperature as real)  as temperature_c,
    cast(humidity as real)     as humidity_pct,
    cast(vibration as real)    as vibration_level,
    cast(battery as integer)   as battery_pct,
    cast(latitude as real)     as latitude,
    cast(longitude as real)    as longitude,
    upper(trim(door_status))   as door_status,
    upper(trim(spoilage_risk)) as spoilage_risk_flag,
    timestamp                  as event_timestamp
from {{ source('atmosync_raw', 'sensor_data') }}
where container_id is not null
  and temperature is not null
