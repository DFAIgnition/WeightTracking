-- Get cost_per_gram of whatever sku was running at the start of the shift
-- (or default to an average of all skus, if nothing else can be found)
select top 1 cost_per_gram from (
select g.event_dt, sc.cost_per_lb, (sc.cost_per_lb / 453.592010498047) as cost_per_gram
from [weight].dbo.giveaway g 
join [weight].dbo.sku_cost sc on (g.site_id = sc.site_id and g.event_dt between sc.effective_start_dt and sc.effective_end_dt and g.sku_id = sc.sku_id)
where event_dt between :start_dt and :end_dt
union all
select dateadd(year,-10,current_timestamp) as event_dt, avg(cost_per_lb) as cost_per_lb, (avg(cost_per_lb) / 453.592010498047) as cost_per_gram
from [weight].dbo.sku_cost
where site_id=:site_id
and :start_dt between effective_start_dt and effective_end_dt 
) as bob
order by event_dt desc
