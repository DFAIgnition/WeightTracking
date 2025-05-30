SELECT 	l.*
FROM 	weight.dbo.line as l
WHERE	(weight_reject_tag is not null or metal_reject_tag is not null)


