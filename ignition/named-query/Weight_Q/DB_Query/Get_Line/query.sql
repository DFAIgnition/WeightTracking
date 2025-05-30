SELECT 			l.site_id,
				l.line_id,
				t.type_id,
				t.type_name,
				l.line_name,
				l.line_desc,
				l.line_weight_min,
				l.line_weight_max,
				l.line_material,
				l.starr_unit_id,
				l.metal_reject_tag,
				l.metal_reject_tag_type,
				l.weight_reject_tag,
				l.weight_reject_tag_type
				
FROM 			weight.dbo.line as l

INNER JOIN 		weight.dbo.type AS t ON l.type_id = t.type_id

WHERE			(:site_id IS NULL OR l.site_id = :site_id);

