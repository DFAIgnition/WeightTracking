SELECT 
    time_start,
    weight_avg, 
    weight_sum, 
    weight_max,
    weight_min, 
    [count], 
    pct_out_of_range, 
    standard_deviation, 
    weight_range, 
    weight_diff,
    percentile25,
    percentile50,
    percentile75,
    sp,
    sp_high,
    sp_low,
    sp_plc,
    sp_low_plc,
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
    ELSE CAST(material AS NVARCHAR(MAX)) -- Also cast the ELSE branch for consistency if material could be numeric here
    END
FROM 
    weight.dbo.aggregated a
	join weight.dbo.scale s on a.scale_id = s.scale_id
	join weight.dbo.filler f on s.filler_id = f.filler_id

    
WHERE 
    time_start >= :start AND 
    time_start < DATEADD(DAY, 10, :start) AND
    (:scale_id = 0 or s.scale_id = :scale_id )AND 
    f.line_id = :line_id AND 
	material = :material
ORDER BY 
    time_start;
