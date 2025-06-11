SELECT distinct l.*
FROM weight.dbo.scale s
	JOIN weight.dbo.filler f on (s.filler_id = f.filler_id)
	JOIN weight.dbo.line l on (f.line_id = l.line_id)
where l.site_id = :site_id
and (s.scale_id = :scale_id or :scale_id = 0)