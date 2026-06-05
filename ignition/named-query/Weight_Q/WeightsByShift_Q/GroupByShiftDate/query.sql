SELECT
    a.shift_date,
        
    SUM([count]) AS 'count',
    
    case when SUM([count]) > 0 then ((SUM(a.weight_sum) / SUM([count]))/:unit_conversion) else 0 end AS 'weight_avg',
    
    SUM(a.weight_diff) /:total_conversion AS 'weight_diff',
    SUM(a.weight_sum) /:total_conversion AS 'weight_sum',
    
    CASE 
    	WHEN SUM([total_count]) > 0 
    		then (SUM( (a.pct_weight_under/100) * total_count)/ SUM([total_count]))*100 
    	else 
    		0 
    	end as 'pct_weight_under',
    CASE 
    	WHEN SUM([total_count]) > 0 
    		then (SUM( (a.pct_weight_over/100) * total_count)/ SUM([total_count]))*100
    	else
    		0 
    	end as 'pct_weight_over',
    
	sum(r.metal_count) as 'metal_rejects', 
	sum(r.weight_count) as 'weight_rejects' 

FROM weight.dbo.aggregated a
	join weight.dbo.scale s on a.scale_id = s.scale_id
	join weight.dbo.filler f on s.filler_id = f.filler_id
	LEFT JOIN weight.dbo.rejects r on (r.line_id = f.line_id and r.time_start = a.time_start and r.material = a.material) 
WHERE ((0 = :scale_id and f.is_line_total = 0) or a.scale_id = :scale_id)
AND a.shift_date >= :shift_date_start
and a.shift_number is not null
--and total_count > 0
AND f.line_id = :line_id
GROUP BY
    a.shift_date  
ORDER BY a.shift_date desc