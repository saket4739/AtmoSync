-- Spoilage Arbitrage
--
-- For each container's LATEST reading, compares price across every
-- candidate market and computes a "net arbitrage value": the price
-- advantage of rerouting, discounted by how much quality has already been
-- lost (a half-spoiled shipment doesn't capture full premium pricing even
-- at a higher-priced market).
--
-- This is the table the trader-facing dashboard (Superset) reads from --
-- it directly answers "which container should I reroute, and where?"

with ranked_readings as (
    select
        *,
        row_number() over (
            partition by container_id
            order by reading_seq desc
        ) as rn
    from {{ ref('spoilage_degradation') }}
),

latest_reading as (
    select *
    from ranked_readings
    where rn = 1
),

-- avocado is the only commodity simulated today; hardcode the join key
-- here so this model still works on sqlite without a commodity column on
-- sensor_data. Swap for a real join key once multiple commodities exist.
priced as (
    select
        lr.*,
        cp.market_id,
        m.market_name,
        cp.price_per_kg
    from latest_reading lr
    cross join {{ source('atmosync_raw', 'commodity_prices') }} cp
    join {{ source('atmosync_raw', 'markets') }} m
        on m.market_id = cp.market_id
    where cp.commodity = 'AVOCADO'
),

primary_price as (
    select price_per_kg as primary_price_per_kg
    from priced
    where market_id = 'MKT-PRIMARY'
    limit 1
)

select
    p.container_id,
    p.event_timestamp        as last_reading_at,
    p.temperature_c,
    p.quality_remaining_pct,
    p.quality_tier,
    p.market_id,
    p.market_name,
    p.price_per_kg,
    pp.primary_price_per_kg,
    round(p.price_per_kg - pp.primary_price_per_kg, 2) as price_advantage_per_kg,
    round(
        (p.price_per_kg - pp.primary_price_per_kg) * (p.quality_remaining_pct / 100.0),
        2
    ) as net_arbitrage_value_per_kg,
    case
        when p.market_id != 'MKT-PRIMARY'
             and (p.price_per_kg - pp.primary_price_per_kg) * (p.quality_remaining_pct / 100.0) > 5
             and p.quality_tier != 'CRITICAL'
        then 1 else 0
    end as reroute_recommended
from priced p
cross join primary_price pp
order by p.container_id, net_arbitrage_value_per_kg desc
