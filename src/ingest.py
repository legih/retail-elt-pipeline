"""Load raw Olist CSV files into the PostgreSQL landing zone."""
import logging
import sys
import pandas as pd
from sqlalchemy import text

from config import RAW_DATA_DIR, get_engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

CSV_TO_TABLE = {
    "olist_customers_dataset.csv": "customers",
    "olist_geolocation_dataset.csv": "geolocation",
    "olist_order_items_dataset.csv": "order_items",
    "olist_order_payments_dataset.csv": "order_payments",
    "olist_order_reviews_dataset.csv": "order_reviews",
    "olist_orders_dataset.csv": "orders",
    "olist_products_dataset.csv": "products",
    "olist_sellers_dataset.csv": "sellers",
    "product_category_name_translation.csv": "product_category_translation",
}

SCHEMA = "raw"
CHUNK_SIZE = 10_000


def create_schema(engine) -> None:
    """Create the raw schema if it does not already exist."""
    with engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}"))
    logger.info("Schema '%s' is ready", SCHEMA)


def load_csv(engine, csv_name: str, table_name: str) -> int:
    """Load one CSV into the raw schema. Returns the row count."""
    csv_path = RAW_DATA_DIR / csv_name

    if not csv_path.exists():
        raise FileNotFoundError(f"Missing input file: {csv_path}")

    df = pd.read_csv(csv_path)
    df.to_sql(
        name=table_name,
        con=engine,
        schema=SCHEMA,
        if_exists="replace",
        index=False,
        chunksize=CHUNK_SIZE,
        method="multi",
    )
    logger.info("Loaded %-28s -> %s.%s (%d rows)",
                csv_name, SCHEMA, table_name, len(df))
    return len(df)


def main() -> None:
    engine = get_engine()
    create_schema(engine)

    total_rows = 0
    failures = []

    for csv_name, table_name in CSV_TO_TABLE.items():
        try:
            total_rows += load_csv(engine, csv_name, table_name)
        except Exception as exc:
            logger.error("FAILED %s: %s", csv_name, exc)
            failures.append(csv_name)

    logger.info("Ingestion finished: %d tables, %d rows total",
                len(CSV_TO_TABLE) - len(failures), total_rows)

    if failures:
        logger.error("Failed files: %s", ", ".join(failures))
        sys.exit(1)


if __name__ == "__main__":
    main()