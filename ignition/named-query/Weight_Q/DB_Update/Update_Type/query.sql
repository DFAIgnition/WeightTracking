UPDATE weight.dbo.type

SET type_name = :type_name, fill_type = :fill_type
    
WHERE type_id = :type_id; 
