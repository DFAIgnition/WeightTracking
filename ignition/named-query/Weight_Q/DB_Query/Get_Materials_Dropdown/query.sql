select distinct material as 'value', material as 'label'
from weight.dbo.aggregated 
where (0 = :scale_id or scale_id = :scale_id)
order by material