SELECT 
    time_start,
    weight_avg, 
    weight_sum, 
    weight_max,
    weight_min, 
    count, 
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
    material
FROM 
    weight.dbo.aggregated
WHERE 
    scale_id = :scale_id AND 
    time_start >= :start AND 
    time_start < DATEADD(DAY, 1, :start)
ORDER BY 
    time_start;
