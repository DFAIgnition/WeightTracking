insert into weight.dbo.manual_losses
	(line_id, shift_id,  shift_date, shift_number, loss_grams, loss_per_hour, cost_per_hour, edited_dt, edited_by)
values (:line_id, :shift_id, :shift_date, :shift_number, :loss_grams, :loss_per_hour, :cost_per_hour, current_timestamp, :edited_by)