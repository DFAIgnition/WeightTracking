SELECT 
    CASE 
        WHEN 
            -- weight exists
            EXISTS (
                SELECT 1
                FROM weight.dbo.scale
                WHERE (scale_id = :scale_id OR :scale_id = 0)
                  AND scale_weight IS NOT NULL
                  AND scale_weight <> ''
            )
            AND
            -- giveaway does NOT exist
            NOT EXISTS (
                SELECT 1
                FROM weight.dbo.giveaway_config
                WHERE line_id = :line_id
                  AND weight_target_tag IS NOT NULL
                  AND weight_target_tag <> ''
            )
            AND
            -- ❗ NEW: fail if any filler has no SP and no tag
            NOT EXISTS (
                SELECT 1
                FROM weight.dbo.filler f
                WHERE f.line_id = :line_id
                  AND (
                        (f.filler_sp_tag IS NULL OR f.filler_sp_tag = '')
                        AND (f.filler_sp IS NULL OR f.filler_sp = 0)
                  )
            )
        THEN 1 
        ELSE 0
    END AS weight_without_giveaway;