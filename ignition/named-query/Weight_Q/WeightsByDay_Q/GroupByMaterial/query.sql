DECLARE @is_utc bit = CASE 
    WHEN DATEDIFF(second, GETUTCDATE(), GETDATE()) = 0 THEN 1 
    ELSE 0 
END

;WITH localised_aggregated AS (
    SELECT
        CAST(
            CASE 
                WHEN @is_utc = 1
                    THEN a.time_start AT TIME ZONE 'UTC' AT TIME ZONE :timezone
                ELSE
                    a.time_start AT TIME ZONE :timezone
            END
        AS datetime2(0)) AS local_time_start, 
		CAST(
            CASE 
                WHEN @is_utc = 1
                    THEN FORMAT(a.time_start AT TIME ZONE 'UTC' AT TIME ZONE :timezone, 'yyyy-MM-dd')
                ELSE
                   FORMAT(a.time_start AT TIME ZONE :timezone, 'yyyy-MM-dd')
            END
        AS nvarchar(32)) AS 'date', 
		CAST(
            CASE 
                WHEN @is_utc = 1
                    THEN FORMAT(a.time_start AT TIME ZONE 'UTC' AT TIME ZONE :timezone, 'MMM dd, yyyy')
                ELSE
                   FORMAT(a.time_start AT TIME ZONE :timezone, 'MMM dd, yyyy')
            END
        AS nvarchar(32)) AS 'display_date',		
		*
    from weight.dbo.aggregated a
    where a.material != 'All'
	AND a.time_start >= :start_dt
	AND a.time_start < :end_dt
	and total_count > 0

)

			SELECT
				a.material,
			    SUM([count]) AS 'count',
			    
			    case when SUM([count]) > 0 then ((SUM(a.weight_sum) / SUM([count]))/:unit_conversion) else 0 end AS 'weight_avg',
			    
			    SUM(a.weight_diff) /:total_conversion AS 'weight_diff',
			    SUM(a.weight_sum) /:total_conversion AS 'weight_sum',
			    (SUM( (a.pct_weight_under/100) * total_count)/ SUM([total_count]))*100 as 'pct_weight_under',
			    (SUM( (a.pct_weight_over/100) * total_count)/ SUM([total_count]))*100 as 'pct_weight_over',
			   (
			            SELECT material_description
			            FROM system.dbo.materials m
			            WHERE m.material_number = TRY_CAST(a.material AS INT)
			        ) AS material_description,
				sum(r.metal_count) as 'metal_rejects', 
				sum(r.weight_count) as 'weight_rejects' 
			
			FROM localised_aggregated as a
				join weight.dbo.scale s on a.scale_id = s.scale_id
				join weight.dbo.filler f on s.filler_id = f.filler_id
				LEFT JOIN weight.dbo.rejects r on (r.line_id = f.line_id and r.time_start = a.time_start and r.material = a.material) 
			WHERE ((0 = :scale_id and f.is_line_total = 0) or a.scale_id = :scale_id)
			AND f.line_id = :line_id
			GROUP BY
			    a.material
			ORDER BY a.material 