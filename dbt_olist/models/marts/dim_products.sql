with products as (

    select * from {{ ref('stg_products') }}

),

translation as (

    select * from {{ source('raw', 'product_category_translation') }}

),

joined as (

    select
        products.product_id,
        products.category_name,
        translation.product_category_name_english as category_name_english,
        products.weight_g,
        products.length_cm,
        products.height_cm,
        products.width_cm

    from products
    left join translation
        on products.category_name = translation.product_category_name

)

select * from joined