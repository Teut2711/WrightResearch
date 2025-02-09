import sqlite3
import pandas as pd
from pathlib import Path

db_path = Path("data/trades.db")


def fetch_client_orders() -> pd.DataFrame:
    """
    Extracts client orders from the SQLite database and returns them as a Pandas DataFrame.

    Args:
        db_path (Path): Path to the SQLite database.

    Returns:
        pd.DataFrame: DataFrame containing client orders.
    """
    column_mapping = {
        "UCC": "client_id",
        "ISIN": "isin",
        "Direction": "buy_sell",
        "Quantity": "quantity",
    }

    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query("SELECT * FROM trades;", conn)
        df.drop(columns=["Ticker"], inplace=True)
        df = df.rename(columns=column_mapping)
        df[column_mapping["Direction"]] = df[column_mapping["Direction"]].map(
            {"Buy": "B", "Sell": "S"}
        )
        df["order_date"] = pd.to_datetime(df["order_date"]).dt.date

    return df
