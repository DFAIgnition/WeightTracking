delete from weight.dbo.aggregated
where scale_id = :scale_id
and time_start >= :start_dt and time_start < :end_dt