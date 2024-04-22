SELECT  time_start ,weight_avg, weight_sum, weight_max,weight_min, count , pct_out_of_range , standard_deviation , weight_range , weight_diff 
FROM weight.dbo.aggregated
WHERE scale_id =  :scale_id 
order by time_start