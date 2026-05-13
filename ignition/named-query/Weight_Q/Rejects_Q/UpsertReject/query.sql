

IF @@ROWCOUNT = 0
INSERT INTO weight.dbo.rejects 
(
    line_id, 
    time_start, 
    metal_count, 
    weight_count, 
    material, 
    po_number,
    metal_test_count,
    metal_actual_count
)
VALUES 
(
    :line_id, 
    :time_start, 
    :metal_count, 
    :weight_count, 
    :material, 
    :po_number,
    :metal_test_count,
    :metal_actual_count
);
