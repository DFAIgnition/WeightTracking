SELECT 		l.line_id,l.line_name,l.type_name,l.tag_material,l.site_id,
			f.filler_id,f.filler_name,f.filler_unit,f.filler_tolerance,f.filler_sp_high,f.filler_sp,f.filler_sp_low,f.tag_sp_high,f.tag_sp,f.tag_sp_low,
			f.tag_metal,f.tag_reject,f.tag_reject_metal,f.tag_reject_over,f.tag_reject_under,
			f.tag_metal_value,f.tag_reject_value,f.tag_reject_metal_value,f.tag_reject_over_value,f.tag_reject_under_value,
			s.scale_id,s.scale_name,s.tag_weight
FROM 		weight.dbo.line AS l
INNER JOIN 	weight.dbo.filler AS f ON l.site_id = f.site_id
INNER JOIN 	weight.dbo.scale AS s ON l.site_id = s.site_id
WHERE 		l.site_id = :site_id