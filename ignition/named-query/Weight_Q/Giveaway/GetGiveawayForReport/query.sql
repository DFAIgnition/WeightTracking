SELECT
    -- Time bucket
    DATEADD(hour, calc.shift_start_hour, calc.bucket_time) AS bucket_start,

    g.sku_id,
    s.sku_code,
    s.sku_description,

    SUM(g.delta_target_grams)   AS target_grams,
    SUM(g.delta_actual_grams)   AS actual_grams,
    SUM(g.delta_giveaway_grams) AS giveaway_grams,

    -- 🔥 Cost (per lb)
    AVG(scost.cost_per_lb) AS cost_per_lb

FROM weight.dbo.giveaway g

-- 🔧 Map scale_id → filler_id
INNER JOIN weight.dbo.scale sc
    ON sc.filler_id = g.filler_id

-- 🔧 Cost join (time-aware)
LEFT JOIN weight.dbo.sku_cost scost
    ON scost.sku_id = g.sku_id
    AND g.event_dt >= scost.effective_start_dt
    AND g.event_dt < scost.effective_end_dt

-- 🔥 Parameter handling (Ignition-safe)
CROSS APPLY (
    SELECT
        CAST(:shift_start_hour AS INT) AS shift_start_hour,
        CAST(:bucket_hours AS INT)     AS bucket_hours
) p

CROSS APPLY (
    SELECT
        DATEADD(
            hour,
            (DATEDIFF(hour, 0, DATEADD(hour, -p.shift_start_hour, g.event_dt)) / p.bucket_hours) * p.bucket_hours,
            0
        ) AS bucket_time,
        p.shift_start_hour
) calc

LEFT JOIN weight.dbo.sku_type s
    ON g.sku_id = s.sku_id

WHERE
    sc.scale_id = :scale_id
    AND g.line_id = :line_id
    AND g.event_dt BETWEEN :start_dt AND :end_dt
    AND (g.quality_flag IS NULL OR g.quality_flag = 0)

GROUP BY
    calc.bucket_time,
    calc.shift_start_hour,
    g.sku_id,
    s.sku_code,
    s.sku_description

ORDER BY
    bucket_start,
    s.sku_code