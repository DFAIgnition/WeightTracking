SELECT
    sc.sku_cost_id,
    sc.sku_id,
    st.sku_code,
    st.sku_description,
    sc.effective_start_dt,
    sc.effective_end_dt,
    sc.cost_per_lb,
    CAST(sc.sku_cost_id AS VARCHAR(50)) AS all_sku_cost_ids   -- 🔥 single row case
FROM weight.dbo.sku_cost sc
JOIN weight.dbo.sku_type st
    ON st.sku_id = sc.sku_id
WHERE sc.site_id = :site_id
  AND :mode = 0   -- SKU mode

UNION ALL

SELECT
    0 AS sku_cost_id,
    0 AS sku_id,
    'ALL' AS sku_code,
    'All SKUs' AS sku_description,
    sc.effective_start_dt,
    sc.effective_end_dt,
    AVG(sc.cost_per_lb) AS cost_per_lb,

    -- 🔥 THIS is the key fix
    STRING_AGG(CAST(sc.sku_cost_id AS VARCHAR(50)), ',') AS all_sku_cost_ids

FROM weight.dbo.sku_cost sc
WHERE sc.site_id = :site_id
  AND :mode = 1   -- COMBINED mode
GROUP BY
    sc.effective_start_dt,
    sc.effective_end_dt

ORDER BY
    effective_start_dt DESC;