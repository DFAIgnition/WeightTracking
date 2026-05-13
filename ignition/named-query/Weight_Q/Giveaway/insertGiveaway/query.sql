MERGE weight.dbo.giveaway_tag_state AS t
USING
(
    SELECT
        :line_id AS line_id,
        :filler_id AS filler_id,
        :sku_id AS sku_id,
        :campaign_id AS campaign_id,
        ISNULL(:campaign_id, N'') AS campaign_key
) AS s
ON  t.line_id = s.line_id
AND t.sku_id  = s.sku_id
AND t.campaign_key = s.campaign_key
WHEN MATCHED THEN
    UPDATE SET
        last_event_dt     = :event_dt,
        last_target_grams = :cur_target_grams,
        last_actual_grams = :cur_actual_grams,
        filler_id         = :filler_id,
        campaign_id       = :campaign_id
WHEN NOT MATCHED THEN
    INSERT
    (
        line_id, filler_id, sku_id, campaign_id,
        last_event_dt, last_target_grams, last_actual_grams
    )
    VALUES
    (
        :line_id, :filler_id, :sku_id, :campaign_id,
        :event_dt, :cur_target_grams, :cur_actual_grams
    );