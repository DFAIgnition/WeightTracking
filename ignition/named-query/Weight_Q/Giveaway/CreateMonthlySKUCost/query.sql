DECLARE @current_month_start DATE = DATEFROMPARTS(YEAR(GETDATE()), MONTH(GETDATE()), 1);
DECLARE @next_month_start DATE = DATEADD(MONTH, 1, @current_month_start);
DECLARE @prev_month_start DATE = DATEADD(MONTH, -1, @current_month_start);

DECLARE @rows_inserted INT = 0;
DECLARE @rows1 INT = 0;
DECLARE @rows2 INT = 0;

-- Insert from previous month
INSERT INTO weight.dbo.sku_cost (
    sku_id,
    effective_start_dt,
    effective_end_dt,
    cost_per_lb,
    comment,
    site_id
)
SELECT
    sm.sku_id,
    @current_month_start,
    DATEADD(DAY, -1, @next_month_start),
    sc.cost_per_lb,
    sc.comment,
    sm.site_id
FROM weight.dbo.sku_map sm
JOIN weight.dbo.sku_cost sc
    ON sc.site_id = sm.site_id
   AND sc.sku_id = sm.sku_id
   AND sc.effective_start_dt = @prev_month_start
WHERE sm.is_active = 1
  AND NOT EXISTS (
        SELECT 1
        FROM weight.dbo.sku_cost existing
        WHERE existing.site_id = sm.site_id
          AND existing.sku_id = sm.sku_id
          AND existing.effective_start_dt = @current_month_start
    );

SET @rows1 = @@ROWCOUNT;

-- Fallback insert
INSERT INTO weight.dbo.sku_cost (
    sku_id,
    effective_start_dt,
    effective_end_dt,
    cost_per_lb,
    comment,
    site_id
)
SELECT
    sm.sku_id,
    @current_month_start,
    DATEADD(DAY, -1, @next_month_start),
    3.00,
    'Auto-generated default',
    sm.site_id
FROM weight.dbo.sku_map sm
WHERE sm.is_active = 1
  AND NOT EXISTS (
        SELECT 1
        FROM weight.dbo.sku_cost existing
        WHERE existing.site_id = sm.site_id
          AND existing.sku_id = sm.sku_id
          AND existing.effective_start_dt = @current_month_start
    )
  AND NOT EXISTS (
        SELECT 1
        FROM weight.dbo.sku_cost sc
        WHERE sc.site_id = sm.site_id
          AND sc.sku_id = sm.sku_id
          AND sc.effective_start_dt = @prev_month_start
    );

SET @rows2 = @@ROWCOUNT;

SET @rows_inserted = @rows1 + @rows2;

SELECT @rows_inserted AS rows_inserted;