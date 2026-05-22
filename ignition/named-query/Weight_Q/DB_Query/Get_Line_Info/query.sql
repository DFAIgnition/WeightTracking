SELECT 			l.site_id,
				t.type_id,
				t.type_name,
				l.line_name,
				l.line_desc,
				l.line_weight_min,
				l.line_weight_max,
				l.line_material,
				l.metal_reject_tag,
				l.metal_reject_tag_type,
				l.weight_reject_tag,
				l.weight_reject_tag_type,
				l.exclude_out_of_range,
				l.assume_weight_rejects,
				
				l.shifts_per_day, 
				l.shift_length, 
				l.shift_start
				
FROM 			weight.dbo.line as l

INNER JOIN 		weight.dbo.type AS t ON l.type_id = t.type_id

WHERE			(line_id = :line_id );

