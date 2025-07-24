
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
        f2.line_id = 1 -- Filter by the correct line
        AND a2.material != 'All'
        AND a2.time_start >= :start -- Match the main query's time filter
        AND a2.time_start < DATEADD(DAY, 10, :start)
),
-- Step 2: Now, build the aggregated string from the unique list generated above.
MaterialStrings AS (
    SELECT
        dm.time_start,
        STRING_AGG(
            CAST(dm.material AS NVARCHAR(MAX)) + 
            CASE 
                WHEN dm.po_number IS NOT NULL THEN ' (PO:' + CAST(dm.po_number AS NVARCHAR(MAX)) + ')' 
                ELSE '' 
            END, 
            ', '
        ) AS AggregatedMaterialString
    FROM 
        DistinctMaterials dm
    GROUP BY 
        dm.time_start
)

-- Step 3: The main query remains the same, but now joins to the corrected string aggregation.
SELECT 
    a.time_start,
    SUM(weight_sum) / SUM([count]) AS 'weight_avg',  
    SUM(a.weight_sum) AS 'weight_sum', 
    MAX(a.weight_max) AS 'weight_max',
    MIN(a.weight_min) AS 'weight_min',
    SUM([count]) AS 'count', 
    SUM(r.metal_count) AS 'metal_rejects', 
    SUM(r.weight_count) AS 'weight_rejects',   
    (SUM((a.pct_out_of_range / 100) * [count]) / SUM([count])) * 100 AS 'pct_out_of_range', 
    SUM(a.standard_deviation * [count]) / SUM([count]) AS 'standard_deviation',
    (MAX(a.weight_max) - MIN(a.weight_min)) AS 'weight_range', 
    SUM(a.weight_diff) AS 'weight_diff',
    SUM(a.percentile25 * [count]) / SUM([count]) AS 'percentile25',
    SUM(a.percentile50 * [count]) / SUM([count]) AS 'percentile50',
    SUM(a.percentile75 * [count]) / SUM([count]) AS 'percentile75',
    AVG(a.sp) AS 'sp',
    AVG(a.sp_high) AS 'sp_high',
    AVG(a.sp_low) AS 'sp_low',
    AVG(a.sp_plc) AS 'sp_plc',
    AVG(a.sp_low_plc) AS 'sp_low_plc',
    AVG(a.sp_high_plc) AS 'sp_high_plc',
    'material' = CASE :material -- This should be your parameter
        WHEN 'All' THEN ms.AggregatedMaterialString
        ELSE :material -- If a specific material is selected, just return that value
    END
FROM 
    weight.dbo.aggregated a
    JOIN weight.dbo.scale s ON a.scale_id = s.scale_id
    JOIN weight.dbo.filler f ON s.filler_id = f.filler_id
    LEFT JOIN weight.dbo.rejects r on (r.line_id = f.line_id and r.time_start = a.time_start and r.material = a.material and :scale_id=0) 
    LEFT JOIN MaterialStrings ms ON a.time_start = ms.time_start 
    
WHERE 
    a.time_start >= :start AND 
    a.time_start < DATEADD(DAY, 10, :start)
 AND
    (:scale_id = 0 or s.scale_id = :scale_id )AND 
    f.line_id = :line_id AND 
	a.material = :material
GROUP BY 
    a.time_start,
    ms.AggregatedMaterialString	
ORDER BY 
    time_start;

