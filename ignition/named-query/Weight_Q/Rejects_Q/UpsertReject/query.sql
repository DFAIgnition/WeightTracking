update  weight.dbo.rejects 
set metal_count = :metal_count, 
	weight_count = :weight_count, 
	material = :material
where line_id = :line_id and time_start = :time_start

if @@ROWCOUNT = 0
	insert into weight.dbo.rejects (line_id, time_start, metal_count, weight_count, material)
	values (:line_id, :time_start, :metal_count, :weight_count, :material)
