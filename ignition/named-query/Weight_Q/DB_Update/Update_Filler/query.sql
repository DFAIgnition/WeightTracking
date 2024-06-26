UPDATE weight.dbo.filler

SET line_id = :line_id,
    unit_id = :unit_id,
    filler_name = :filler_name,
    filler_design = :filler_design,
    filler_sp_low = :filler_sp_low,
    filler_sp = :filler_sp,
    filler_sp_high = :filler_sp_high,
    filler_sp_low_tag = :filler_sp_low_tag,
    filler_sp_tag = :filler_sp_tag,
    filler_sp_high_tag = :filler_sp_high_tag,
    filler_reject = :filler_reject,
    filler_reject_cond = :filler_reject_cond,
    filler_metal = :filler_metal,
    filler_metal_cond = :filler_metal_cond,
    filler_reason_over = :filler_reason_over,
    filler_reason_over_cond = :filler_reason_over_cond,
    filler_reason_under = :filler_reason_under,
    filler_reason_under_cond = :filler_reason_under_cond,
    filler_reason_metal = :filler_reason_metal,
    filler_reason_metal_cond = :filler_reason_metal_cond
    
WHERE filler_id = :filler_id;