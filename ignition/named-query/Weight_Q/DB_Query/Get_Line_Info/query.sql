SELECT 			l.site_id,
				t.type_id,
				t.type_name,
				l.line_name,
				l.line_desc,
				l.line_weight_min,
				l.line_weight_max,
				l.line_material
				
FROM 			weight.dbo.line as l

INNER JOIN 		weight.dbo.type AS t ON l.type_id = t.type_id

WHERE			(line_id = :line_id );

