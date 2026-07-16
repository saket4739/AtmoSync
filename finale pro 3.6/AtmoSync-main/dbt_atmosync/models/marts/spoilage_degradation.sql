-- Spoilage Degradation Curve
--
-- Models cumulative quality loss per container as a function of time spent
-- outside the ideal storage band for avocados (4C - 7C). Each reading adds
-- an incremental degradation amount; readings further outside the ideal
-- range degrade quality faster (non-linear curve), and humidity/vibration
-- spikes add a smaller secondary penalty.
--
-- This is a simplified physical model for demo purposes, not a calibrated
-- food-science formula -- swap PARAMS below for real spoilage-rate
-- coefficients if you have them.

with params as (
    select
        4.0  as ideal_temp_low,
        7.0  as ideal_temp_high,
        0.4  as base_decay_pct_per_reading,   -- decay even inside ideal range (normal ripening)
        0.9  as temp_penalty_multiplier,      -- extra decay per degree outside ideal band
        0.05 as humidity_penalty_multiplier,  -- extra decay per % humidity above 85
        0.15 as vibration_penalty_multiplier  -- extra decay per unit vibration above 3

),

readings as (
    select
        s.*,
        row_number() over (
            partition by s.container_id
            order by s.event_timestamp
        ) as reading_seq
    from {{ ref('stg_sensor_data') }} s
),

decay_per_reading as (
    select
        r.*,
        p.base_decay_pct_per_reading
            + (max(0.0, p.ideal_temp_low - r.temperature_c) * p.temp_penalty_multiplier)
            + (max(0.0, r.temperature_c - p.ideal_temp_high) * p.temp_penalty_multiplier)
            + (max(0.0, r.humidity_pct - 85) * p.humidity_penalty_multiplier)
            + (max(0.0, r.vibration_level - 3) * p.vibration_penalty_multiplier)
            as decay_pct
    from readings r
    cross join params p
),

cumulative as (
    select
        *,
        sum(decay_pct) over (
            partition by container_id
            order by reading_seq
            rows between unbounded preceding and current row
        ) as cumulative_decay_pct
    from decay_per_reading
)

select
    id,
    container_id,
    reading_seq,
    temperature_c,
    humidity_pct,
    vibration_level,
    door_status,
    spoilage_risk_flag,
    event_timestamp,
    round(decay_pct, 3)            as decay_pct_this_reading,
    round(cumulative_decay_pct, 2) as cumulative_decay_pct,
    round(
        max(0.0, 100.0 - cumulative_decay_pct), 2
    ) as quality_remaining_pct,
    case
        when (100.0 - cumulative_decay_pct) >= 70 then 'GOOD'
        when (100.0 - cumulative_decay_pct) >= 40 then 'DEGRADING'
        else 'CRITICAL'
    end as quality_tier
from cumulative
