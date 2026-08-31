select
    d.year,
    d.month,
    count(distinct f.order_id) as orders,
    round(sum(f.total_item_value), 2) as revenue
from analytics.fact_order_items f
join analytics.dim_date d
    on f.purchased_at::date = d.date_day
where f.order_status = 'delivered'
group by d.year, d.month
order by d.year, d.month;