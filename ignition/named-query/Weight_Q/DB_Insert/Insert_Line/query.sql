INSERT INTO weight.dbo.line

(type_id, site_id, line_name, line_material, line_weight_min, line_weight_max, line_desc, starr_unit_id, metal_reject_tag, metal_reject_tag_type, weight_reject_tag, weight_reject_tag_type) 

VALUES 

(:type_id, :site_id, :line_name , :line_material, :line_weight_min, :line_weight_max, :line_desc, :starr_unit_id, :metal_reject_tag, :metal_reject_tag_type, :weight_reject_tag, :weight_reject_tag_type)