SELECT 			f.*,s.scale_id,s.scale_name,s.scale_weight,l.site_id,l.line_name
				
FROM 			weight.dbo.filler as f

INNER JOIN 		weight.dbo.line AS l ON f.line_id = l.line_id
INNER JOIN 		weight.dbo.scale AS s ON f.filler_id = s.filler_id

WHERE			(:site_id IS NULL OR l.site_id = :site_id)
	AND 		(l.line_id = :line_id);