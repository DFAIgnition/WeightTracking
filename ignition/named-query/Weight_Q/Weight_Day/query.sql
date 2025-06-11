SELECT 
    a.time_start,
    a.weight_avg, 
    a.weight_sum, 
    a.weight_max,
    a.weight_min, 
    [count], 
	r.metal_count as 'metal_rejects', 
	r.weight_count as 'weight_rejects',    
    a.pct_out_of_range, 
    a.standard_deviation, 
    a.weight_range, 
    a.weight_diff,
    a.percentile25,
    a.percentile50,
    a.percentile75,
    a.sp,
    a.sp_high,
    a.sp_low,
   a.sp_plc,
   a.sp_low_plc,
    sp_high_plc,
   'material' =
    CASE :material
    WHEN 'All' THEN
        (
            SELECT STRING_AGG(
                       -- Explicitly cast all parts to VARCHAR
                       CAST(material AS NVARCHAR(MAX))
                       + CASE
                             WHEN a2.po_number IS NOT NULL THEN ' (PO:' + CAST(a2.po_number AS NVARCHAR(MAX)) + ')'
                             ELSE ''
                         END,
                       ', '
                   )
            FROM weight.dbo.aggregated a2
            WHERE a2.scale_id = a.scale_id
            AND a2.time_start = a.time_start
            AND a2.material != 'All'
        )
    ELSE CAST(a.material AS NVARCHAR(MAX)) -- Also cast the ELSE branch for consistency if material could be numeric here
    END
FROM 
    weight.dbo.aggregated a
	join weight.dbo.scale s on a.scale_id = s.scale_id
	join weight.dbo.filler f on s.filler_id = f.filler_id
	LEFT JOIN weight.dbo.rejects r on (r.line_id = f.line_id and r.time_start = a.time_start and r.material = a.material and :scale_id=0) 
    
WHERE 
    a.time_start >= :start AND 
    a.time_start < DATEADD(DAY, 10, :start) AND
    (:scale_id = 0 or s.scale_id = :scale_id )AND 
    f.line_id = :line_id AND 
	a.material = :material
ORDER BY 
    time_start;
