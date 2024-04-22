SELECT			filler_id
FROM 			weight.dbo.filler
WHERE			line_id = 		:line_id
			AND	unit_id = 		:unit_id 
			AND	filler_name = 	:filler_name 