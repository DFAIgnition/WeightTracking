SELECT m.sku_id
FROM weight.dbo.sku_map m
WHERE m.site_id = :site_id
  AND m.line_id = :line_id
  AND m.recipe_no = :recipe
  AND m.is_active = 1