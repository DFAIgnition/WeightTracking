-- Manual losses by month
select DATEFROMPARTS(YEAR(a.time_start), MONTH(a.time_start), 1) AS production_month, u.unit_name, u.unit_id, 
    sum(ml.loss_per_hour) as giveaway_grams, 
    (sum(ml.loss_per_hour/u.unit_conversion)) as giveaway_weight,
    (sum(ml.cost_per_hour)) as giveaway_cost,
    sum(a.weight_sum) as actual_grams, 
    sum(a.weight_sum/u.unit_conversion) as actual_weight
from [weight].dbo.aggregated a
JOIN [weight].dbo.scale s on (a.scale_id=s.scale_id)
JOIN [weight].dbo.filler f on (s.filler_id=f.filler_id)

JOIN [weight].dbo.manual_losses ml on (ml.line_id=f.line_id and ml.shift_date = a.shift_date and ml.shift_number=a.shift_number)
JOIN [weight].dbo.unit u on u.unit_id = :unit_id
where f.line_id=:line_id
and a.material = 'All'

  AND DATEFROMPARTS(YEAR(a.time_start), MONTH(a.time_start), 1) BETWEEN 
        DATEFROMPARTS(YEAR(:start_dt), MONTH(:start_dt), 1)
    AND DATEFROMPARTS(YEAR(:end_dt), MONTH(:end_dt), 1)
    
group by DATEFROMPARTS(YEAR(a.time_start), MONTH(a.time_start), 1),u.unit_name, u.unit_id

