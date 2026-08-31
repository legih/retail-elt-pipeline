# Retail ELT Pipeline

I built this to learn data engineering properly instead of just watching tutorials.
It takes the Olist Brazilian e-commerce dataset (9 CSV files, ~1.5M rows) and turns
it into a star schema you can actually query.

Stack: Python, PostgreSQL, dbt, Docker, Power BI.

## What it does

CSVs get loaded into a `raw` schema in Postgres by a Python script. dbt then cleans
them up in a staging layer and builds the fact and dimension tables on top. Power BI
connects to the marts layer at the end.

I went with ELT instead of ETL — load the raw data first, transform it inside the
warehouse. The reason is practical: when I got the revenue calculation wrong the
first time, I just changed the SQL and re-ran it. If I'd transformed during load,
I'd have had to reload everything from the CSVs.

## The data model

| Table | Rows |
|---|---|
| fact_order_items | 112,650 |
| dim_customers | 99,441 |
| dim_products | 32,951 |
| dim_sellers | 3,095 |
| dim_date | 1,461 |

The fact table is one row per **product in an order**, not per order. This matters —
an order can have several products from different sellers at different prices. If I'd
picked the order level, that detail would be gone for good and I couldn't do any
product analysis.

## Things I got wrong and fixed

**Postal codes as integers.** pandas loaded them as `bigint`, so `01310` became `1310`.
Leading zero gone. Would have broken every join on zip code later. Now they're `varchar`.

**Money as float.** Started with float, switched to `numeric`. Floating point rounding
errors on financial data isn't something you want to explain to anyone.

**Everything was text.** The CSV loader imports every column as text. All the type
casting happens in staging now.

## Testing

28 dbt tests run every time the pipeline builds:

- unique + not_null on all primary keys
- relationships tests on every foreign key in the fact table (so if a product_id in
  the fact doesn't exist in dim_products, the build fails)
- accepted_values on order_status

I use `dbt build` rather than `dbt run` followed by `dbt test`, because build tests
each model before the ones depending on it get created. Bad data stops where it starts.

## What I found in the data

Ran a monthly revenue query and a few things jumped out.

November 2017 hit 1,153,364 in revenue — 53% higher than October. That's Black Friday.

Revenue grew about 20x from late 2016 to early 2018.

The edges of the dataset are junk. September 2016 has exactly one order. December 2016
has one. November 2016 doesn't exist at all. I excluded these from any trend analysis
because including them would make the growth curve meaningless.

## Running it

You need Docker and Python 3.11+. Download the
[Olist dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) from
Kaggle — it's not in this repo.

```bash
# Postgres
docker run --name de-postgres -e POSTGRES_PASSWORD=devpass \
  -e POSTGRES_USER=dev -e POSTGRES_DB=warehouse \
  -p 5432:5432 -d postgres:16

# Python deps
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```

Create a `.env` in the root with DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD.
Put the 9 CSVs in `data/raw/`. Then:

```bash
cd src && python ingest.py
cd ../dbt_olist && dbt build
```

dbt also needs a `profiles.yml` in `~/.dbt/`. Credentials stay out of git in both places.

## Layout

```
src/            Python ingestion (config.py, ingest.py)
dbt_olist/
  models/
    staging/    one model per source table, cleaned
    marts/      fact + dimensions
analysis/       ad-hoc queries
data/raw/       CSVs (gitignored)
```

## Not done yet

**Airflow.** The pipeline runs manually right now. Next step is scheduling it with
retries and backfills.

**Incremental loads.** `ingest.py` does a full reload every time — drops the table and
rewrites it. Fine for 1.5M rows, useless at 100M. I'd need to switch to loading only
new or changed records.

**Payments and reviews.** Both tables are sitting in the raw schema unused. The
interesting question there is whether late deliveries drag down review scores.
