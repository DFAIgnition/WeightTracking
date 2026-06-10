DECLARE @is_utc BIT = CASE 
    WHEN DATEDIFF(second, GETUTCDATE(), GETDATE()) = 0 THEN 1 
    ELSE 0 
END

;WITH hourly_giveaway AS (
    -- Step 1: aggregate to hourly buckets in UTC, NO timezone conversion yet
    SELECT
        DATEADD(hour, DATEDIFF(hour, 0, g.event_dt), 0) AS event_hour_utc,
        g.site_id,
        g.line_id,
        g.filler_id,
        g.sku_id,
        SUM(g.delta_target_grams)   AS target_grams,
        SUM(g.delta_actual_grams)   AS actual_grams,
        SUM(g.delta_giveaway_grams) AS giveaway_grams
    FROM [weight].dbo.giveaway g
    WHERE g.line_id = :line_id
      AND g.event_dt >= :start_dt
      AND g.event_dt <  :end_dt
      AND g.quality_flag = 0
    GROUP BY
        DATEADD(hour, DATEDIFF(hour, 0, g.event_dt), 0),
        g.site_id,
        g.line_id,
        g.filler_id,
        g.sku_id
),
local_giveaway AS (
    -- Step 2: AT TIME ZONE runs on hourly rows only
    -- Also compute shift_number here, before the next aggregation
    SELECT
        CAST(
            CASE 
                WHEN @is_utc = 1
                    THEN h.event_hour_utc AT TIME ZONE 'UTC' AT TIME ZONE :timezone
                ELSE
                    h.event_hour_utc AT TIME ZONE :timezone
            END
        AS DATETIME2(0)) AS local_event_dt,
        CAST(
            CASE 
                WHEN @is_utc = 1
                    THEN DATEADD(hour, -:day_start, h.event_hour_utc) AT TIME ZONE 'UTC' AT TIME ZONE :timezone
                ELSE
                    DATEADD(hour, -:day_start, h.event_hour_utc) AT TIME ZONE :timezone
            END
        AS DATETIME2(0)) AS local_shift_date,
        CAST(h.event_hour_utc AS DATE) AS event_date,
        h.site_id,
        h.line_id,
        h.filler_id,
        h.sku_id,
        h.target_grams,
        h.actual_grams,
        h.giveaway_grams
    FROM hourly_giveaway h
),
local_giveaway_with_shift AS (
    -- Step 3: calculate shift number from the local_shift_date-adjusted time
    -- Done as a separate CTE so we can reference local_shift_date cleanly
    SELECT
        *,
        -- Hour within the production day (0-23 after the day_start offset is applied)
        DATEDIFF(hour,
            CAST(CAST(local_shift_date AS DATE) AS DATETIME2),  -- midnight of production date
            local_shift_date                                      -- actual local time
        ) AS hour_of_production_day,
        (DATEDIFF(hour,
            CAST(CAST(local_shift_date AS DATE) AS DATETIME2),
            local_shift_date
        ) / :shift_length) + 1  AS shift_number
    FROM local_giveaway
),
aggregated AS (
    -- Step 4: roll up to daily+shift buckets before joins
    SELECT
        DATEFROMPARTS(YEAR(l.local_shift_date), MONTH(l.local_shift_date), DAY(l.local_shift_date)) AS production_date,
        l.shift_number,
        l.site_id,
        l.line_id,
        l.filler_id,
        l.sku_id,
        l.event_date,
        SUM(l.target_grams)   AS target_grams,
        SUM(l.actual_grams)   AS actual_grams,
        SUM(l.giveaway_grams) AS giveaway_grams
    FROM local_giveaway_with_shift l
    GROUP BY
        DATEFROMPARTS(YEAR(l.local_shift_date), MONTH(l.local_shift_date), DAY(l.local_shift_date)),
        l.shift_number,
        l.site_id,
        l.line_id,
        l.filler_id,
        l.sku_id,
        l.event_date
)
SELECT
    concat(a.production_date,':',a.shift_number) as shift, 
    a.production_date,
    a.shift_number,
    a.site_id,
    a.line_id,
    a.filler_id,
    s.sku_code,
    s.sku_description,
    u.unit_name,
    u.unit_id,
    SUM(a.target_grams)   AS target_grams,
    SUM(a.actual_grams)   AS actual_grams,
    SUM(a.giveaway_grams) AS giveaway_grams,
    SUM(a.giveaway_grams) / 453.59237                                                           AS giveaway_lbs,
    SUM(a.actual_grams)   / NULLIF(s.nominal_net_grams, 0)                                      AS packages_produced,
    SUM(a.giveaway_grams) / NULLIF(SUM(a.actual_grams), 0) * 100                               AS giveaway_percent,
    SUM(a.giveaway_grams) / NULLIF(SUM(a.actual_grams) / NULLIF(s.nominal_net_grams, 0), 0)    AS giveaway_per_package_grams,
    SUM((a.giveaway_grams / 453.59237) * sc.cost_per_lb)
        / NULLIF(SUM(a.giveaway_grams / 453.59237), 0)                                          AS cost_per_lb,
    SUM((a.giveaway_grams / 453.59237) * sc.cost_per_lb)                                        AS giveaway_dollars,
    SUM((a.giveaway_grams / 453.59237) * sc.cost_per_lb)
        / NULLIF(SUM(a.actual_grams) / NULLIF(s.nominal_net_grams, 0), 0)                       AS giveaway_dollars_per_package,
    SUM(a.giveaway_grams / u.unit_conversion)                                                   AS giveaway_weight,
    SUM(a.actual_grams   / u.unit_conversion)                                                   AS actual_weight,
    SUM(a.target_grams   / u.unit_conversion)                                                   AS target_weight
FROM aggregated a
LEFT JOIN weight.dbo.sku_type s
    ON a.sku_id = s.sku_id
LEFT JOIN weight.dbo.sku_cost sc
    ON  sc.site_id = a.site_id
    AND sc.sku_id  = a.sku_id
    AND a.event_date >= sc.effective_start_dt
    AND a.event_date <= ISNULL(sc.effective_end_dt, '9999-12-31')
LEFT JOIN [weight].dbo.manual_losses ml on (ml.line_id=a.line_id and ml.shift_date = a.production_date and ml.shift_number=a.shift_number)
    
JOIN weight.dbo.unit u
    ON u.unit_id = :unit_id
GROUP BY
    a.production_date,
    a.shift_number,
    a.site_id,
    a.line_id,
    a.filler_id,
    s.sku_code,
    s.sku_description,
    s.nominal_net_grams,
    u.unit_name,
    u.unit_id
ORDER BY a.production_date DESC, a.shift_number desc
OPTION (RECOMPILE)