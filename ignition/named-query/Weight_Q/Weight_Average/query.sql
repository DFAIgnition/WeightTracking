
SELECT	time_start, 
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

		STRING_AGG(material, ', ') AS material
FROM weight.dbo.aggregated
WHERE scale_id = :scale_id
AND time_start >= DATEADD(month, -11, DATEADD(month, DATEDIFF(month, 0, GETDATE()), 0))
group by time_start

ORDER BY time_start;
