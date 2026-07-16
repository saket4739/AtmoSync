-- Paste these into Superset's SQL Lab, run, then "Save as Dataset" to use
-- in charts without needing extra dbt models.

-- 1. Latest reading per container (one row each, for status widgets)
SELECT *
FROM spoilage_degradation sd
WHERE reading_seq = (
    SELECT MAX(reading_seq)
    FROM spoilage_degradation sd2
    WHERE sd2.container_id = sd.container_id
);

-- 2. Active reroute alerts only, ranked by value
SELECT
    container_id,
    market_name,
    price_per_kg,
    primary_price_per_kg,
    price_advantage_per_kg,
    net_arbitrage_value_per_kg,
    quality_remaining_pct,
    quality_tier,
    last_reading_at
FROM spoilage_arbitrage
WHERE reroute_recommended = 1
ORDER BY net_arbitrage_value_per_kg DESC;

-- 3. Containers currently in CRITICAL quality tier (urgent attention)
SELECT *
FROM spoilage_degradation sd
WHERE quality_tier = 'CRITICAL'
  AND reading_seq = (
      SELECT MAX(reading_seq)
      FROM spoilage_degradation sd2
      WHERE sd2.container_id = sd.container_id
  );

-- 4. Fleet summary KPIs (for a Big Number row at the top of the dashboard)
SELECT
    COUNT(DISTINCT container_id) AS total_containers,
    SUM(CASE WHEN quality_tier = 'CRITICAL' THEN 1 ELSE 0 END) AS critical_containers,
    ROUND(AVG(quality_remaining_pct), 1) AS avg_fleet_quality_pct
FROM spoilage_degradation sd
WHERE reading_seq = (
    SELECT MAX(reading_seq)
    FROM spoilage_degradation sd2
    WHERE sd2.container_id = sd.container_id
);
