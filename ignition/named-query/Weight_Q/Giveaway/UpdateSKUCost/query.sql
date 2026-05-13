UPDATE weight.dbo.sku_cost
SET 
    cost_per_lb = :cost_per_lb,
    comment     = :comment
WHERE sku_cost_id IN (
    SELECT x.i.value('.', 'INT')
    FROM (
        SELECT CAST('<i>' + REPLACE(:sku_cost_ids, ',', '</i><i>') + '</i>' AS XML) AS xml_data
    ) t
    CROSS APPLY xml_data.nodes('/i') x(i)
);