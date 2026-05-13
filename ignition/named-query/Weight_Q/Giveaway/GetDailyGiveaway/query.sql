SELECT
    CAST(v.production_date AS DATE) AS production_date,
    v.sku_code,

    v.giveaway_grams / u.unit_conversion AS giveaway_weight,
    v.actual_grams   / u.unit_conversion AS actual_weight,

    v.giveaway_percent,
    v.giveaway_dollars,

    u.unit_name,
    u.unit_id

FROM weight.dbo.vw_giveaway_daily v
JOIN weight.dbo.unit u
    ON u.unit_id = :unit_id

WHERE v.line_id = :line_id
  AND v.production_date BETWEEN :start_dt AND :end_dt

ORDER BY production_date, sku_code