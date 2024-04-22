INSERT INTO weight.dbo.line

(type_id, site_id, line_name, line_material, line_weight_min, line_weight_max, line_desc) 

VALUES 

(:type_id, :site_id, :line_name , :line_material, :line_weight_min, :line_weight_max, :line_desc)