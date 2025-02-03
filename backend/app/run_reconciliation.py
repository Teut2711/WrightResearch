from app.extract_trades import extract_excel_from_eml
from app.reconcile_trades import reconcile_trades
from app.generate_reports import generate_reports
from app.database import (
    create_task,
    fetch_client_orders,
    insert_client_orders,
    insert_broker_trades,
    insert_reconciliation_results,
    update_task_status,
)
from pydantic.types import UUID


def run_reconciliation(task_id: UUID):
    create_task(task_id)
    try:
        client_orders = fetch_client_orders()
        broker_trades = extract_excel_from_eml()

        insert_client_orders(client_orders)
        insert_broker_trades(broker_trades)

        reconciliation_results = reconcile_trades(client_orders, broker_trades)
        insert_reconciliation_results(reconciliation_results)

        generate_reports(reconciliation_results)
        update_task_status(task_id, "success")
    except Exception as e:  # noqa
        update_task_status(task_id, "failed", str(e))
