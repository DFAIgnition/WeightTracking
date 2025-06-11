select top 1 * from starr.dbo.unit_states
where unit_id = :unit_id 
and start_dt >= :start_dt
and start_dt < dateadd(day,2,:start_dt)
and state_id=1
order by start_dt