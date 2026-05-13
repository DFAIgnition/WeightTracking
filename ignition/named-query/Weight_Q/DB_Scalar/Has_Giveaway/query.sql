SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1
            FROM weight.dbo.giveaway_config
            WHERE line_id = :line_id
              AND weight_target_tag IS NOT NULL
              AND weight_target_tag  <> ''
        )
        THEN 1 ELSE 0
    END AS has_wgiveaway_tag;