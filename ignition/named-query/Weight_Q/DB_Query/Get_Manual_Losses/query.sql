select s.*, 
	concat(s.shift_date,'_',s.shift_number) as shift_id,
m.manual_loss_id, m.loss_grams, m.loss_per_hour, m.edited_dt, m.edited_by, u.*,
l.shift_length, l.shifts_per_day, l.shift_start
from 
	(select distinct shift_date, shift_number, line_id 
	from [weight].dbo.aggregated a
	join [weight].dbo.scale s on (a.scale_id = s.scale_id)
	join [weight].dbo.filler f on (s.filler_id = f.filler_id)
	where f.line_id=:line_id
	and material='All'
	and time_start >= dateadd(day,-:days, current_timestamp)
	) as s
LEFT JOIN [weight].dbo.manual_losses m on (s.shift_date = m.shift_date and s.shift_number = m.shift_number)
JOIN  [weight].dbo.line l on s.line_id = l.line_id
JOIN [weight].dbo.unit u on u.unit_name = :units

order by shift_id desc