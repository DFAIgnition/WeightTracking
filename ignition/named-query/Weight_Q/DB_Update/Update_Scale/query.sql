UPDATE weight.dbo.scale

SET scale_name = :scale_name, 
    scale_weight = :scale_weight, 
    filler_id = :filler_id
    
WHERE scale_id = :scale_id; 
