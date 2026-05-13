SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1
            FROM weight.dbo.line
            WHERE line_id = :line_id
              AND metal_reject_tag IS NOT NULL
              AND metal_reject_tag <> ''
        )
        THEN 1 ELSE 0
    END AS has_metal_tag;