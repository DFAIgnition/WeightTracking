INSERT INTO weight.dbo.aggregated 
			
			(scale_id, time_start, count, weight_avg,
   			weight_sum, weight_diff, pct_weight_over, pct_weight_under,
    		pct_out_of_range, standard_deviation, variance, weight_range,
    		weight_max, weight_min, percentile25, percentile50, percentile75,
    		reject_metal,reject_over,reject_under,material,
    		sp_high,sp,sp_low,sp_high_plc,sp_plc,sp_low_plc,design, po_number)
    		
VALUES 
			(:scale_id, :time_start, :count , :weight_avg ,
		 	:weight_sum , :weight_diff , :pct_weight_over , :pct_weight_under, 
		 	:pct_out_of_range, :standard_deviation,  :variance ,  :weight_range,
		 	:weight_max , :weight_min , :percentile25 , :percentile50 , :percentile75 ,
		 	:reject_metal , :reject_over , :reject_under , :material , 
		 	:sp_high , :sp , :sp_low, :sp_high_plc , :sp_plc , :sp_low_plc, :design, :po_number )