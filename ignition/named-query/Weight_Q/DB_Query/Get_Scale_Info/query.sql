SELECT 			f.filler_design, f.filler_sp, u.unit_name, u.unit_conversion,s.scale_name
FROM 			weight.dbo.filler as f
INNER JOIN 		weight.dbo.scale AS s ON f.filler_id = s.filler_id
INNER JOIN 		weight.dbo.unit AS u ON f.unit_id = u.unit_id
WHERE			scale_id =  :scale_id 
or (:scale_id  = 0 and f.line_id = :line_id)
order by s.scale_name