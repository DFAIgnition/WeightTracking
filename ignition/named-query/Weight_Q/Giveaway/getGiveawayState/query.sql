SELECT TOP 1
    giveaway_state_id,
    last_target_grams,
    last_actual_grams
FROM weight.dbo.giveaway_tag_state
WHERE line_id = :line_id
  AND sku_id  = :sku_id
  AND campaign_key = ISNULL(:campaign_id, N'')
ORDER BY last_event_dt DESC