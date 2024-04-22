SELECT COUNT(*) 

FROM 		weight.dbo.line 

WHERE 		type_id = 			:type_id
		AND site_id = 			:site_id
		AND line_name = 		:line_name
