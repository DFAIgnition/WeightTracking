SELECT ISNULL(
    (
        SELECT unit_id
        FROM weight.dbo.unit
        WHERE unit_name = :unit_name
    ),
    (
        SELECT unit_id
        FROM weight.dbo.unit
        WHERE unit_name = 'g'
    )
) AS unit_id