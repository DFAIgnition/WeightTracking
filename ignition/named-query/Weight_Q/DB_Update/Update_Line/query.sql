UPDATE weight.dbo.line

SET type_id = :type_id, 
    site_id = :site_id, 
    line_name = :line_name, 
    line_desc = :line_desc, 
    line_weight_min = :line_weight_min, 
    line_weight_max = :line_weight_max, 
    line_material = :line_material,
    starr_unit_id = :starr_unit_id,
    
    metal_reject_tag = :metal_reject_tag, 
    metal_reject_tag_type = :metal_reject_tag_type,
    metal_test_tag = :metal_test_tag, 
    metal_test_tag_type = :metal_test_tag_type,
	weight_reject_tag = :weight_reject_tag, 
    weight_reject_tag_type = :weight_reject_tag_type,
    exclude_out_of_range = :exclude_out_of_range,
    assume_weight_rejects = :assume_weight_rejects,
    
    shifts_per_day = :shifts_per_day, 
    shift_length = :shift_length, 
    shift_start = :shift_start
    
WHERE line_id = :line_id; 
