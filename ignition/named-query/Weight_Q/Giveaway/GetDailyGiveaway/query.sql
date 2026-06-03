
DECLARE @is_utc bit = CASE 
    WHEN DATEDIFF(second, GETUTCDATE(), GETDATE()) = 0 THEN 1 
    ELSE 0
END

;WITH local_giveaway AS (
    SELECT
        CAST(
            CASE 
                WHEN @is_utc = 1
                    THEN g.event_dt AT TIME ZONE 'UTC' AT TIME ZONE :timezone
                ELSE
                    g.event_dt AT TIME ZONE :timezone
            END
        AS datetime2(0)) AS local_event_dt, *

    
    from [weight].dbo.giveaway g
    where g.line_id=:line_id
	and (g.event_dt >= :start_dt and g.event_dt < :end_dt)
)
select 
   DATEFROMPARTS(YEAR(a.local_event_dt), MONTH(a.local_event_dt), DAY(a.local_event_dt)) AS production_date, 
   
    a.site_id,
    a.line_id,
    a.filler_id,

    s.sku_code,
    s.sku_description,
    
    u.unit_name, u.unit_id,

    SUM(a.delta_target_grams)   AS target_grams,
    SUM(a.delta_actual_grams)   AS actual_grams,
    SUM(a.delta_giveaway_grams) AS giveaway_grams,

    SUM(a.delta_giveaway_grams) / 453.59237                              AS giveaway_lbs,
    SUM(a.delta_actual_grams)   / NULLIF(s.nominal_net_grams, 0)                    AS packages_produced,
    SUM(a.delta_giveaway_grams) / NULLIF(SUM(a.delta_actual_grams), 0) * 100        AS giveaway_percent,

    SUM(a.delta_giveaway_grams)
        / NULLIF(SUM(a.delta_actual_grams) / NULLIF(s.nominal_net_grams, 0), 0)     AS giveaway_per_package_grams,

    -- weighted avg cost
    SUM((a.delta_giveaway_grams / 453.59237) * sc.cost_per_lb)
        / NULLIF(SUM(a.delta_giveaway_grams / 453.59237), 0)             AS cost_per_lb,

    SUM((a.delta_giveaway_grams / 453.59237) * sc.cost_per_lb)           AS giveaway_dollars,

    SUM((a.delta_giveaway_grams / 453.59237) * sc.cost_per_lb)
        / NULLIF(SUM(a.delta_actual_grams) / NULLIF(s.nominal_net_grams, 0), 0)     AS giveaway_dollars_per_package,
    
    SUM(a.delta_giveaway_grams / u.unit_conversion) AS giveaway_weight,
    SUM(a.delta_actual_grams   / u.unit_conversion) AS actual_weight

from local_giveaway as a

LEFT JOIN weight.dbo.sku_type s
    ON a.sku_id = s.sku_id

LEFT JOIN weight.dbo.sku_cost sc
    ON  sc.site_id = a.site_id
    AND sc.sku_id  = a.sku_id
    AND CAST(a.event_dt AS date) >= sc.effective_start_dt
    AND CAST(a.event_dt AS date) <= ISNULL(sc.effective_end_dt, '9999-12-31')

JOIN weight.dbo.unit u
ON u.unit_id = :unit_id

WHERE a.quality_flag = 0

GROUP BY
    a.site_id,
    DATEFROMPARTS(YEAR(a.local_event_dt), MONTH(a.local_event_dt), DAY(a.local_event_dt)),
    a.line_id,
    a.filler_id,
    s.sku_code,
    s.sku_description,
    s.nominal_net_grams,
    u.unit_name, u.unit_id

order by production_date desc
