import sqlite3
import pandas as pd
from pathlib import Path
from typing import Literal, Optional
from pydantic.types import UUID


db_path = Path("data/trades.db")


def create_tables():
    conn = sqlite3.connect(db_path)
    if conn is None:
        raise Exception("Database connection failed")

    cursor = conn.cursor()

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS client_orders (
        order_id TEXT PRIMARY KEY,
        client_id TEXT,
        symbol TEXT,
        quantity INTEGER,
        order_price REAL,
        order_date TEXT
    );
    """
    )

    cursor.execute("PRAGMA table_info(trades);")
    columns = [info[1] for info in cursor.fetchall()]
    if "order_date" not in columns:
        cursor.execute(
            "ALTER TABLE trades ADD COLUMN order_date TEXT DEFAULT '6/12/2024';"
        )

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS broker_trades (
        deal_date TEXT,
        party_code TEXT,
        instrument TEXT,
        isin TEXT,
        buy_sell_flag TEXT,
        quantity INTEGER,
        cost REAL,
        net_amount REAL,
        brokerage_amount REAL,
        settlement_date TEXT,
        stt REAL,
        exchange_code TEXT,
        depository_code TEXT
    );
    """
    )

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS reconciliation_results (
        order_id TEXT,
        client_id TEXT,
        symbol TEXT,
        matched_quantity INTEGER,
        unmatched_quantity INTEGER,
        status TEXT,
        total_cost REAL,
        execution_slippage REAL
    );
    """
    )

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS tasks (
        task_id TEXT PRIMARY KEY default uuid,
        status TEXT,
        reason TEXT DEFAULT NULL
    );
    """
    )

    conn.commit()
    conn.close()


def insert_client_orders(client_orders: pd.DataFrame):
    conn = sqlite3.connect(db_path)
    client_orders.to_sql("client_orders", conn, if_exists="append", index=False)
    conn.close()


def create_task(task_id: UUID):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (task_id, status) VALUES (?, ?)",
        (
            str(task_id),
            "pending",
        ),
    )
    conn.commit()
    conn.close()
    return task_id


def update_task_status(
    task_id: str, status: Literal["failed", "success"], reason=Optional[str]
):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    if reason:
        cursor.execute(
            "UPDATE tasks SET status = ?, reason = ? WHERE task_id = ?",
            (status, reason, task_id),
        )
    else:
        cursor.execute(
            "UPDATE tasks SET status = ? WHERE task_id = ?", (status, task_id)
        )
    conn.commit()
    conn.close()


def insert_broker_trades(broker_trades: pd.DataFrame):
    conn = sqlite3.connect(db_path)
    broker_trades.to_sql("broker_trades", conn, if_exists="append", index=False)
    conn.close()


def insert_reconciliation_results(reconciliation_results: pd.DataFrame):
    conn = sqlite3.connect(db_path)
    reconciliation_results.to_sql(
        "reconciliation_results", conn, if_exists="append", index=False
    )
    conn.close()


def fetch_client_orders() -> pd.DataFrame:
    """
    Extracts client orders from the SQLite database and returns them as a Pandas DataFrame.

    Args:
        db_path (Path): Path to the SQLite database.

    Returns:
        pd.DataFrame: DataFrame containing client orders.
    """
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query("SELECT * FROM client_orders", conn)
    return df
