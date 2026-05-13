WITH BaseAgg AS (
    SELECT
        a.time_start,
        SUM(a.weight_sum)                                  AS weight_sum,
        MAX(a.weight_max)                                  AS weight_max,
        MIN(a.weight_min)                                  AS weight_min,
        SUM(a.count)                                       AS count,
        SUM(a.total_count)                                 AS total_count,
        SUM(a.weight_diff)                                 AS weight_diff,
        SUM((a.pct_out_of_range / 100.0) * a.total_count) AS pct_num,
        SUM(a.total_count)                                 AS pct_den,
        SUM(POWER(a.standard_deviation, 2))                AS std_sum,
        MAX(a.standard_deviation)                          AS og_stddev
    FROM weight.dbo.aggregated a
    JOIN weight.dbo.scale  s ON a.scale_id  = s.scale_id
    JOIN weight.dbo.filler f ON s.filler_id = f.filler_id
    WHERE
        ((:scale_id = 0 AND f.is_line_total = 0) OR a.scale_id = :scale_id)
        AND f.line_id = :line_id
        AND a.time_start >= DATEADD(month, -:months, DATEADD(month, DATEDIFF(month, 0, :end_dt), 0))
        AND a.time_start <  DATEADD(day, 1, EOMONTH(:end_dt))
        AND a.material != 'All'                            -- never use pre-aggregated All row
        AND (:material = 'All' OR a.material = :material)
    GROUP BY a.time_start
),

RejectAgg AS (
    SELECT
        r.time_start,
        SUM(ISNULL(r.metal_count,        0)) AS metal_count,
        SUM(ISNULL(r.metal_test_count,   0)) AS metal_test_count,
        SUM(ISNULL(r.metal_actual_count, 0)) AS metal_actual_count,
        SUM(ISNULL(r.weight_count,       0)) AS weight_count
    FROM weight.dbo.rejects r
    WHERE r.line_id  = :line_id
      AND r.material != 'All'                            -- never use pre-aggregated All row
      AND (:material = 'All' OR r.material = :material)
    GROUP BY r.time_start
)

SELECT
    b.time_start,
    CASE WHEN b.count > 0 THEN (b.weight_sum / b.count) ELSE 0 END AS weight_avg,
    b.weight_sum,
    b.weight_max,
    b.weight_min,
    b.count,
    b.total_count,
    (b.weight_max - b.weight_min)                                   AS weight_range,
    b.weight_diff,
    (b.pct_num / NULLIF(b.pct_den, 0)) * 100                       AS pct_out_of_range,
    SQRT(b.std_sum)                                                 AS standard_deviation,
    b.og_stddev,
    ISNULL(r.metal_count,        0)                                 AS metal_count,
    ISNULL(r.metal_test_count,   0)                                 AS metal_test_count,
    ISNULL(r.metal_actual_count, 0)                                 AS metal_actual_count,
    ISNULL(r.weight_count,       0)                                 AS weight_rejects,
    CASE WHEN :material = 'All' THEN 'All' ELSE :material END       AS material
FROM BaseAgg b
LEFT JOIN RejectAgg r ON r.time_start = b.time_start
ORDER BY b.time_start;