
SELECT	a.time_start, 
		(sum(weight_sum) / sum([count])) as 'weight_avg', 
		sum(weight_sum) as 'weight_sum', 
		max(weight_max) as 'weight_max', 
		min(weight_min) as 'weight_min', 
		sum([count]) as 'count', 
		(max(weight_max) - max(weight_min)) as 'weight_range',
	
		sum(weight_diff)  as 'weight_diff',

		(sum(((pct_out_of_range/100) * [count]))/sum([count]))*100 as  pct_out_of_range,
		sqrt(sum(power(standard_deviation,2))) as 'standard_deviation', 
		max(standard_deviation) as 'og_stddev', 
		sum(r.metal_count) as 'metal_rejects', 
		sum(r.weight_count) as 'weight_rejects',
		STRING_AGG(a.material, ', ') AS material
FROM weight.dbo.aggregated a 
	join weight.dbo.scale s on a.scale_id = s.scale_id
	join weight.dbo.filler f on s.filler_id = f.filler_id
	LEFT JOIN weight.dbo.rejects r on (r.line_id = f.line_id and r.time_start = a.time_start and r.material = a.material and :scale_id=0) 
WHERE (:scale_id = 0  or a.scale_id = :scale_id)
AND f.line_id = :line_id
--AND time_start >= DATEADD(month, -11, DATEADD(month, DATEDIFF(month, 0, GETDATE()), 0))
AND a.time_start >= DATEADD(month, -11, DATEADD(month, DATEDIFF(month, 0, :end_dt), 0))
AND a.time_start <  DATEADD(day,1,EOMONTH(:end_dt))
and (a.material = :material)
group by a.time_start

ORDER BY a.time_start;
