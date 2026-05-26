update weight.dbo.manual_losses
set loss_grams = :loss_grams, 
	loss_per_hour = :loss_per_hour, 
	cost_per_hour = :cost_per_hour,
	edited_dt = current_timestamp, 
	edited_by = :edited_by
where shift_id = :shift_id and line_id = :line_id