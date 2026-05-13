SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1
            FROM weight.dbo.line
            WHERE line_id = :line_id
              AND weight_reject_tag IS NOT NULL
              AND weight_reject_tag <> ''
        )
        THEN 1 ELSE 0
    END AS has_reject_tag;