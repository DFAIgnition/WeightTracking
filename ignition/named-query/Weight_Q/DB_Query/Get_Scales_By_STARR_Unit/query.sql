SELECT 		s.scale_id, l.*
FROM 		weight.dbo.line AS l
INNER JOIN 	weight.dbo.filler AS f ON l.line_id = f.line_id
INNER JOIN 	weight.dbo.scale AS s ON f.filler_id = s.filler_id
WHERE 		l.starr_unit_id =:starr_unit_id