SELECT 		l.line_id,l.line_name,l.line_type,l.tag_material,l.site_id,
			f.filler_id,f.filler_name,f.filler_unit,f.filler_tolerance,f.filler_sp_high,f.filler_sp,f.filler_sp_low,f.tag_sp_high,f.tag_sp,f.tag_sp_low,
			f.tag_metal,f.tag_reject,f.tag_reject_metal,f.tag_reject_over,f.tag_reject_under,
			f.tag_metal_value,f.tag_reject_value,f.tag_reject_metal_value,f.tag_reject_over_value,f.tag_reject_under_value,
			s.scale_id,s.scale_name,s.tag_weight
FROM 		weight.dbo.line AS l
INNER JOIN 	weight.dbo.filler AS f ON l.line_id = f.line_id
INNER JOIN 	weight.dbo.scale AS s ON f.filler_id = s.filler_id
WHERE 		l.site_id = :site_id
			AND l.line_type =  :type AND l.line_name =  :name  AND f.filler_name =  :filler  AND s.scale_name =  :scale