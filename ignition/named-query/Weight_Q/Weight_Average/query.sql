SELECT time_start, weight_avg, weight_sum, weight_max, weight_min, count, pct_out_of_range, standard_deviation, weight_range, weight_diff,material
FROM weight.dbo.aggregated
WHERE scale_id = :scale_id
AND time_start >= DATEADD(month, -11, DATEADD(month, DATEDIFF(month, 0, GETDATE()), 0))
ORDER BY time_start;