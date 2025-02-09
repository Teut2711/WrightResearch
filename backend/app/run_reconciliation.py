import traceback
from app.extract_trades import extract_excel_from_eml
from app.generate_reports import generate_reports
from app.database import (
    create_task,
    insert_client_orders,
    insert_broker_trades,
    insert_reconciliation_results,
    update_task_status,
)
from app.fetch_client_orders import fetch_client_orders
from pydantic.types import UUID

from app.reconcile_trades import reconcile_trades
from app.fetch_emls import fetch_gmail_emails


def run_reconciliation(task_id: UUID):
    create_task(task_id)
    fetch_gmail_emails()

    try:
        client_orders = fetch_client_orders()
        broker_trades = extract_excel_from_eml()

        if client_orders is not None and not client_orders.empty:
            insert_client_orders(client_orders)
        else:
            raise Exception("No client orders found")

        if broker_trades is not None and not broker_trades.empty:
            insert_broker_trades(broker_trades)
        else:
            raise Exception("No broker trades found")

        reconciliation_results = reconcile_trades(client_orders, broker_trades)
        insert_reconciliation_results(reconciliation_results)

        generate_reports(reconciliation_results)
        update_task_status(task_id, "success", reason=None)
    except Exception as e:  # noqa
        error_traceback = traceback.format_exc()
        # Update the task status with the error message and traceback
        update_task_status(
            task_id, "failed", reason=f"Error: {str(e)}\nTraceback:\n{error_traceback}"
        )
