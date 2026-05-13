SELECT
    giveaway_config_id,
    site_id,
    line_id,
    filler_id,
    use_campaign_id, 
    jobid_tag,
    recipe_tag,
    weight_target_tag,
    weight_actual_tag,
    reset_threshold_grams,
    max_delta_grams
FROM weight.dbo.giveaway_config
WHERE is_enabled = 1
ORDER BY site_id, line_id, filler_id;