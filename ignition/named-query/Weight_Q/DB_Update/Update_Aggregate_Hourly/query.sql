UPDATE 		weight.dbo.aggregated 
SET 
		    [count] = :count, 
		    weight_avg = :weight_avg,
		    weight_sum = :weight_sum, 
		    weight_diff = :weight_diff, 
		    pct_weight_over = :pct_weight_over, 
		    pct_weight_under = :pct_weight_under,
		    pct_out_of_range = :pct_out_of_range, 
		    standard_deviation = :standard_deviation, 
		    variance = :variance, 
		    weight_range = :weight_range,
		    weight_max = :weight_max, 
		    weight_min = :weight_min, 
		    percentile25 = :percentile25, 
		    percentile50 = :percentile50, 
		    percentile75 = :percentile75,
		    reject_metal = :reject_metal, 
		    reject_over = :reject_over, 
		    reject_under = :reject_under, 
		    material = :material, 
		    sp_high = :sp_high, 
		    sp = :sp, 
		    sp_low = :sp_low, 
		    sp_high_plc = :sp_high_plc, 
		    sp_plc = :sp_plc, 
		    sp_low_plc = :sp_low_plc, 
		    design = :design
WHERE 
		    scale_id = :scale_id AND 
		    time_start = :time_start AND 
		    material = :material 

