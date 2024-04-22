UPDATE weight.dbo.unit

SET unit_name = 			:unit_name,
	unit_conversion = 		:unit_conversion 
    
WHERE unit_id = :unit_id; 
