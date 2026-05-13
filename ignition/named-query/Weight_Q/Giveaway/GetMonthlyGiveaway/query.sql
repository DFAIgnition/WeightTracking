SELECT
    v.production_month,
    v.sku_code,

    -- ✅ Converted values
    v.giveaway_grams / u.unit_conversion AS giveaway_weight,
    v.actual_grams   / u.unit_conversion AS actual_weight,

    -- unchanged
    v.giveaway_percent,
    v.giveaway_dollars,

    -- ✅ unit metadata
    u.unit_name,
    u.unit_id

FROM weight.dbo.vw_giveaway_monthly v
JOIN weight.dbo.unit u
    ON u.unit_id = :unit_id

WHERE v.line_id = :line_id
  AND v.production_month BETWEEN 
        DATEFROMPARTS(YEAR(:start_dt), MONTH(:start_dt), 1)
    AND DATEFROMPARTS(YEAR(:end_dt), MONTH(:end_dt), 1)