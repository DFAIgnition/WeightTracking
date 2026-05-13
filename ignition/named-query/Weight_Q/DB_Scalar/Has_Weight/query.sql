SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1
            FROM weight.dbo.scale
            WHERE scale_id = :scale_id OR :scale_id = 0
              AND scale_weight IS NOT NULL
              AND scale_weight <> ''
        )
        THEN 1 ELSE 0
    END AS has_weight_tag;