select material, po_number, sum(cast(((pct_out_of_range/100)*total_count)+0.5 as int)) as reject_count
from weight.dbo.aggregated
where scale_id in (select scale_id from weight.dbo.line where line_id=1)
and time_start =:time_start 
and material != 'All'
group by time_start, material,po_number
order by time_start 