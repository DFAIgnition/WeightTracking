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
        (	select STRING_AGG(material, ', ') 
    	from weight.dbo.aggregated a2 
    	where a2.scale_id = a.scale_id 
    	and a2.time_start = a.time_start 
    	and a2.material != 'All')
    ELSE material
    END
FROM 
    weight.dbo.aggregated a
WHERE 
    time_start >= :start AND 
    time_start < DATEADD(DAY, 1, :start) AND
    scale_id = :scale_id AND 
	material = :material
ORDER BY 
    time_start;
