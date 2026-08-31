with source as (

    select * from {{ source('raw', 'order_items') }}

),

renamed as (

    select
        order_id,
        order_item_id as item_number,  
        product_id,
        seller_id,
        shipping_limit_date::timestamp as shipping_limit_at,
        price::numeric,
        freight_value::numeric as freight
    from source

)

select * from renamed