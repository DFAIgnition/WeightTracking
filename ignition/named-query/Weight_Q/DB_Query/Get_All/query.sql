SELECT 			f.filler_id,
				u.unit_id,
				l.line_id,
				t.type_id,
				t.fill_type,
				s.scale_id,
				t.type_name,
				l.line_name,
				l.line_material,
				l.starr_unit_id,
				l.site_id,
				u.unit_name,
				u.unit_conversion,
				f.filler_design,
				f.filler_metal,
				f.filler_metal_cond,
				f.filler_name,
				f.filler_reason_metal,
				f.filler_reason_metal_cond,
				f.filler_reason_over,
				f.filler_reason_over_cond ,
				f.filler_reason_under ,
				f.filler_reason_under_cond ,
				f.filler_reject ,
				f.filler_reject_cond ,			
				f.filler_sp , 
				f.filler_sp_high ,
				f.filler_sp_high_tag ,
				f.filler_sp_low ,
				f.filler_sp_low_tag ,
				f.filler_sp_tag,
				s.scale_name,
				s.scale_weight
				
FROM 			weight.dbo.filler as f

INNER JOIN 		weight.dbo.unit AS u ON f.unit_id = u.unit_id
INNER JOIN 		weight.dbo.line AS l ON f.line_id = l.line_id
INNER JOIN 		weight.dbo.type AS t ON l.type_id = t.type_id
INNER JOIN 		weight.dbo.scale AS s ON f.filler_id = s.filler_id
  
WHERE 			(:site_id IS NULL OR :site_id = 0 OR l.site_id = :site_id)
AND 			(:scale_id IS NULL OR :scale_id = 0 OR s.scale_id = :scale_id)

ORDER BY 		s.scale_id

