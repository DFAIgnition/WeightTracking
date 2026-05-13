-- Step 1: Create a CTE to get a unique list of materials and PO numbers for each time slot on the line.
WITH DistinctMaterials AS (
    SELECT DISTINCT
        a2.time_start,
        a2.material,
        a2.po_number
    FROM 
        weight.dbo.aggregated a2
    JOIN weight.dbo.scale s2 ON a2.scale_id = s2.scale_id
    JOIN weight.dbo.filler f2 ON s2.filler_id = f2.filler_id
    WHERE 
        f2.line_id = :line_id
        AND a2.material != 'All'
        AND a2.time_start >= :start
        AND a2.time_start < DATEADD(DAY, 10, :start)
),

-- Step 2: Aggregate material strings
MaterialStrings AS (
    SELECT
        dm.time_start,
        STRING_AGG(
            CAST(dm.material AS NVARCHAR(MAX)) + 
            CASE 
                WHEN dm.po_number IS NOT NULL 
                THEN ' (PO:' + CAST(dm.po_number AS NVARCHAR(MAX)) + ')' 
                ELSE '' 
            END, 
            ', '
        ) AS AggregatedMaterialString
    FROM DistinctMaterials dm
    GROUP BY dm.time_start
),

-- 🔥 Step 3: PRE-AGGREGATE REJECTS (FIXED — NO MATERIAL!)
RejectAgg AS (
    SELECT 
        line_id,
        time_start,
        SUM(ISNULL(metal_count, 0)) AS metal_count,
        SUM(ISNULL(metal_test_count, 0)) AS metal_test_count,
        SUM(ISNULL(metal_actual_count, 0)) AS metal_actual_count,
        SUM(ISNULL(weight_count, 0)) AS weight_count
    FROM weight.dbo.rejects
    GROUP BY line_id, time_start
)

-- Step 4: MAIN QUERY
SELECT 
    a.time_start,

    -- Weight
    CASE 
        WHEN SUM([count]) > 0 
        THEN (SUM(a.weight_sum) / SUM([count])) 
        ELSE 0 
    END AS weight_avg,

    SUM(a.weight_sum) AS weight_sum, 
    MAX(a.weight_max) AS weight_max,
    MIN(a.weight_min) AS weight_min,

    SUM([count]) AS count, 
    SUM([total_count]) AS total_count, 

    -- 🔴 METAL (NOW ALWAYS WORKS)
    SUM(ISNULL(r.metal_count, 0)) AS metal_count,
    SUM(ISNULL(r.metal_test_count, 0)) AS metal_test_count,
    SUM(ISNULL(r.metal_actual_count, 0)) AS metal_actual_count,

    -- Optional backward compatibility
    SUM(ISNULL(r.metal_count, 0)) AS metal_rejects,

    SUM(ISNULL(r.weight_count, 0)) AS weight_rejects,

    -- Stats
    (SUM((a.pct_out_of_range / 100) * [total_count]) / NULLIF(SUM([total_count]), 0)) * 100 AS pct_out_of_range,

    CASE 
        WHEN SUM([count]) > 0 
        THEN (SUM(a.standard_deviation * [count]) / SUM([count])) 
        ELSE 0 
    END AS standard_deviation,

    (MAX(a.weight_max) - MIN(a.weight_min)) AS weight_range, 
    SUM(a.weight_diff) AS weight_diff,

    CASE 
        WHEN SUM([count]) > 0 
        THEN (SUM(a.percentile25 * [count]) / SUM([count])) 
        ELSE 0 
    END AS percentile25,

    CASE 
        WHEN SUM([count]) > 0 
        THEN (SUM(a.percentile50 * [count]) / SUM([count])) 
        ELSE 0 
    END AS percentile50,

    CASE 
        WHEN SUM([count]) > 0 
        THEN (SUM(a.percentile75 * [count]) / SUM([count])) 
        ELSE 0 
    END AS percentile75,

    -- Setpoints
    AVG(a.sp) AS sp,
    AVG(a.sp_high) AS sp_high,
    AVG(a.sp_low) AS sp_low,
    AVG(a.sp_plc) AS sp_plc,
    AVG(a.sp_low_plc) AS sp_low_plc,
    AVG(a.sp_high_plc) AS sp_high_plc,

    -- Material output
    CASE :material
        WHEN 'All' THEN ms.AggregatedMaterialString
        ELSE :material
    END AS material

FROM weight.dbo.aggregated a
JOIN weight.dbo.scale s ON a.scale_id = s.scale_id
JOIN weight.dbo.filler f ON s.filler_id = f.filler_id

-- 🔥 FIXED JOIN (NO MATERIAL = NO DATA LOSS)
LEFT JOIN RejectAgg r 
    ON r.line_id = f.line_id 
    AND r.time_start = a.time_start 

LEFT JOIN MaterialStrings ms 
    ON a.time_start = ms.time_start 

WHERE 
    a.time_start >= :start 
    AND a.time_start < DATEADD(DAY, 10, :start)

    AND ((:scale_id = 0 AND f.is_line_total = 0) OR s.scale_id = :scale_id)
    AND f.line_id = :line_id
    AND a.material = :material

GROUP BY 
    a.time_start,
    ms.AggregatedMaterialString

ORDER BY 
    a.time_start;