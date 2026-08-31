with order_items as (

    select * from {{ ref('stg_order_items') }}

),

orders as (

    select * from {{ ref('stg_orders') }}

),

joined as (

    select
        order_items.order_id,
        order_items.item_number,
        order_items.product_id,
        order_items.seller_id,
        orders.customer_id,
        orders.order_status,
        orders.purchased_at::date as purchased_at,
        orders.delivered_at,
        orders.estimated_delivery_at,
        order_items.price,
        order_items.freight,
        order_items.price + order_items.freight as total_item_value

    from order_items
    inner join orders
        on order_items.order_id = orders.order_id

)

select * from joined