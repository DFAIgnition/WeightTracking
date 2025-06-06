delete from weight.dbo.rejects
where line_id = :line_id
and time_start >= :start_dt and time_start < :end_dt