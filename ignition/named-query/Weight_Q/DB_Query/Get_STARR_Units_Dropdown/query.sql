select is_fully_active  as is_active,
concat(p.plant_name, ' - ', l.line_name, ' - ', u.unit_name ) as 'label', uc.unit_id as 'value'
from starr.dbo.unit_config uc
JOIN system.dbo.units u on (uc.unit_id = u.unit_id)
JOIN system.dbo.lines l on (u.line_id = l.line_id)
JOIN system.dbo.plants p on (l.plant_id = p.plant_id)
CROSS APPLY (select min(d) as is_fully_active from (VALUES (cast(uc.is_active as int)), (cast(u.is_active as int)), (cast(l.is_active as int)), (cast(p.is_active as int))) as a(d)) A
WHERE p.site_id = :site_id
order by 1,2,3