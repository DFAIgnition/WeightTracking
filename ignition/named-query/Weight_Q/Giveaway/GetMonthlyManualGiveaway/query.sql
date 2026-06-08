DECLARE @is_utc bit = CASE 
    WHEN DATEDIFF(second, GETUTCDATE(), GETDATE()) = 0 THEN 1 
    ELSE 0 
END

;WITH local_times AS (
    SELECT
        CAST(
            CASE 
                WHEN @is_utc = 1
                    THEN a.time_start AT TIME ZONE 'UTC' AT TIME ZONE :timezone
                ELSE
                    a.time_start AT TIME ZONE :timezone
            END
        AS datetime2(0)) AS time_start,
        
        CAST(
            CASE 
                WHEN @is_utc = 1
                    THEN dateadd(hour, -:day_start, a.time_start) AT TIME ZONE 'UTC' AT TIME ZONE :timezone
                ELSE
                    dateadd(hour, -:day_start, a.time_start) AT TIME ZONE :timezone
            END
        AS datetime2(0)) AS local_shift_date,
                
        u.unit_name, u.unit_id, f.line_id,a.shift_date, a.shift_number,u.unit_conversion,
        sum(a.weight_sum) as actual_grams, 
        sum(a.weight_sum/u.unit_conversion) as actual_weight,
        count(*) as filler_count
    from [weight].dbo.aggregated a
    JOIN [weight].dbo.scale s on (a.scale_id=s.scale_id)
    JOIN [weight].dbo.filler f on (s.filler_id=f.filler_id)
    JOIN [weight].dbo.unit u on u.unit_id = :unit_id
    where f.line_id=:line_id
    and a.material = 'All'
	
	AND (a.time_start >= :start_dt and a.time_start < :end_dt)
        
    group by  a.time_start,u.unit_name, u.unit_id, f.line_id,a.shift_date, a.shift_number,u.unit_conversion

)

select  
    DATEFROMPARTS(YEAR(a.local_shift_date), MONTH(a.local_shift_date), 1) AS production_month, a.unit_name, a.unit_id, 
    sum(ml.loss_per_hour) as giveaway_grams, 
    (sum(ml.loss_per_hour/a.unit_conversion)) as giveaway_weight,
    (sum(ml.cost_per_hour)) as giveaway_cost,
    sum(a.actual_grams) as actual_grams, 
    sum(a.actual_weight) as actual_weight
from local_times as a
LEFT JOIN [weight].dbo.manual_losses ml on (ml.line_id=a.line_id and ml.shift_date = a.shift_date and ml.shift_number=a.shift_number)

group by DATEFROMPARTS(YEAR(a.local_shift_date), MONTH(a.local_shift_date), 1),a.unit_name, a.unit_id

