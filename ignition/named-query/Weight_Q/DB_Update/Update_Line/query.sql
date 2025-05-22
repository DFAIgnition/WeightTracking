UPDATE weight.dbo.line

SET type_id = :type_id, 
    site_id = :site_id, 
    line_name = :line_name, 
    line_desc = :line_desc, 
    line_weight_min = :line_weight_min, 
    line_weight_max = :line_weight_max, 
    line_material = :line_material,
    starr_unit_id = :starr_unit_id
    
WHERE line_id = :line_id; 
