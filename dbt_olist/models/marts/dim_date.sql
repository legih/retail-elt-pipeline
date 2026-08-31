with date_spine as (

    select generate_series(
        '2016-01-01'::date,
        '2019-12-31'::date,
        '1 day'::interval
    )::date as date_day

)

select
    date_day,
    extract(year  from date_day)::int    as year,
    extract(month from date_day)::int    as month,
    extract(day   from date_day)::int    as day_of_month,
    extract(quarter from date_day)::int  as quarter,
    extract(isodow  from date_day)::int  as day_of_week,
    to_char(date_day, 'Month')           as month_name,
    date_trunc('month',   date_day)::date as first_day_of_month,
    extract(isodow from date_day) in (6, 7) as is_weekend

from date_spine