SELECT COUNT(*) 

FROM 		weight.dbo.scale

WHERE 		filler_id = 	:filler_id
		AND scale_name =	:scale_name
