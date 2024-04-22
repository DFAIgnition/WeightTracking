SELECT 			f.filler_design
				
FROM 			weight.dbo.filler as f

INNER JOIN 		weight.dbo.scale AS s ON f.filler_id = s.filler_id

WHERE			scale_id =  :scale_id 
