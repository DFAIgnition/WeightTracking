SELECT	a.time_start, 
		
	case when SUM([count]) > 0 then ((SUM(a.weight_sum) / SUM([count]))) else 0 end AS weight_avg,
		 
	sum(weight_sum) as weight_sum, 
	max(weight_max) as weight_max, 
	min(weight_min) as weight_min, 
	sum([count]) as count, 
	sum([total_count]) as total_count, 
	(max(weight_max) - max(weight_min)) as weight_range,
	
	sum(weight_diff) as weight_diff,

	(sum(((pct_out_of_range/100) * [total_count])) / NULLIF(sum([total_count]),0)) * 100 as pct_out_of_range,

	sqrt(sum(power(standard_deviation,2))) as standard_deviation, 
	max(standard_deviation) as og_stddev, 

	-- METAL (SAFE)
	SUM(ISNULL(r.metal_count, 0)) as metal_count, 
	SUM(ISNULL(r.metal_test_count, 0)) as metal_test_count,
	SUM(ISNULL(r.metal_actual_count, 0)) as metal_actual_count,
	SUM(ISNULL(r.weight_count, 0)) as weight_rejects,

	a.material

FROM weight.dbo.aggregated a 
JOIN weight.dbo.scale s ON a.scale_id = s.scale_id
JOIN weight.dbo.filler f ON s.filler_id = f.filler_id

LEFT JOIN (
    SELECT 
        line_id,
        time_start,
        material,
        SUM(metal_count) AS metal_count,
        SUM(metal_test_count) AS metal_test_count,
        SUM(metal_actual_count) AS metal_actual_count,
        SUM(weight_count) AS weight_count
    FROM weight.dbo.rejects
    GROUP BY line_id, time_start, material
) r
ON (
    r.line_id = f.line_id 
    AND r.time_start = a.time_start 
    AND (
        r.material = a.material 
        OR r.material = 'All'
    )
)

WHERE ((:scale_id = 0 AND f.is_line_total = 0) OR a.scale_id = :scale_id)
AND f.line_id = :line_id
AND a.time_start >= DATEADD(month, -:months, DATEADD(month, DATEDIFF(month, 0, :end_dt), 0))
AND a.time_start < DATEADD(day,1,EOMONTH(:end_dt))

GROUP BY a.time_start, a.material

ORDER BY a.time_start;