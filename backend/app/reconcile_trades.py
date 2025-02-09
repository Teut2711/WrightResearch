import pandas as pd


def reconcile_trades(
    client_orders: pd.DataFrame, broker_trades: pd.DataFrame
) -> pd.DataFrame:
    """
    Match broker trades with client orders based on:
    - Symbol, Date, and Quantity Matching Logic.
    - Handles Exact Match, Partial Match, Excess Quantity, Pending Orders.
    - Allocates trades proportionally if multiple brokers are involved.

    Returns:
        pd.DataFrame: A DataFrame containing reconciliation results including order status, matched quantities,
        unmatched quantities, and total cost.
    """
    client_orders["filled_qty"] = 0  # Track filled quantities for client orders
    reconciled_trades = []

    # Sort broker trades by 'Buy/Sell Flag' and 'Cost'
    broker_trades = broker_trades.sort_values(
        by=["buy_sell", "cost"], ascending=[True, True]
    )

    # Group client orders and broker trades by symbol and date
    grouped_data = group_orders_and_trades(client_orders, broker_trades)

    # Reconcile each group
    for (isin, date, buy_sell_num), (
        client_group,
        broker_group,
    ) in grouped_data.items():
        reconciled_trades += reconcile_group(client_group, broker_group, isin)

    return pd.DataFrame(reconciled_trades)


def group_orders_and_trades(
    client_orders: pd.DataFrame, broker_trades: pd.DataFrame
) -> dict:
    """
    Groups the client orders and broker trades by 'symbol' and 'order_date' for reconciliation.

    Args:
        client_orders (pd.DataFrame): Client's orders dataframe.
        broker_trades (pd.DataFrame): Broker's trades dataframe.

    Returns:
        dict: A dictionary where keys are tuples of (symbol, order_date, buy_sell_num) and values are tuples of
              (client_group, broker_group).
    """

    # Group client orders and broker trades
    client_grouped = client_orders.groupby(by=["isin", "order_date", "buy_sell"])
    broker_grouped = broker_trades.groupby(by=["isin", "deal_date", "buy_sell"])

    grouped_data = {}
    for (isin, date, buy_sell), client_group in client_grouped:
        if (isin, date, buy_sell) in broker_grouped.groups:
            broker_group = broker_grouped.get_group((isin, date, buy_sell))
            grouped_data[(isin, date, buy_sell)] = (
                client_group,
                broker_group,
            )

    return grouped_data


def reconcile_group(
    client_group: pd.DataFrame, broker_group: pd.DataFrame, symbol: str
) -> list:
    """
    Reconciles a single client-broker group based on matching logic.

    Args:
        client_group (pd.DataFrame): Group of client orders for the current symbol and date.
        broker_group (pd.DataFrame): Group of broker trades for the current symbol and date.
        symbol (str): The symbol of the orders/trades.

    Returns:
        list: A list of reconciliation results for the current group.
    """
    results = []
    total_client_qty = client_group["quantity"].sum()
    total_broker_qty = broker_group["quantity"].sum()

    # Allocate broker trades to client orders proportionally
    for _, client in client_group.iterrows():
        allocated_qty = (client["quantity"] / total_client_qty) * total_broker_qty
        matched_qty = min(allocated_qty, client["quantity"])
        excess_broker_qty = max(0, total_broker_qty - allocated_qty)
        pending_client_qty = max(0, client["quantity"] - allocated_qty)

        status = "matched"
        if excess_broker_qty > 0:
            status = "excess"
        elif pending_client_qty > 0:
            status = "pending"

        # Calculate total cost
        total_cost = calculate_total_cost(
            broker_group["cost"].mean(),
            matched_qty,
            broker_group["brokerage"].sum(),
            broker_group["stt"].sum(),
        )

        # Calculate execution slippage
        if "order_price" in client and matched_qty > 0:
            effective_price = broker_group["net_amount"].sum() / total_broker_qty
            slippage = calculate_slippage(client["order_price"], effective_price)
        else:
            slippage = 0  # Assume no slippage if order_price is not available or matched_qty is 0

        results.append(
            {
                "client_id": client["client_id"],
                "symbol": symbol,
                "matched_quantity": matched_qty,
                "excess_broker_quantity": excess_broker_qty,
                "pending_client_quantity": pending_client_qty,
                "status": status,
                "total_cost": total_cost,
                "slippage": slippage,  # Include slippage in results
            }
        )

    return results


def calculate_total_cost(
    price: float, quantity: int, broker_fee: float, stt: float
) -> float:
    """
    Calculates the total cost of a trade.
    """
    return price * quantity + broker_fee + stt


def calculate_slippage(order_price: float, effective_price: float) -> float:
    """
    Calculates the execution slippage for a trade.

    Args:
        order_price (float): The price the client expected.
        effective_price (float): The effective price at which the trade was executed (Net Amount / Quantity).

    Returns:
        float: The execution slippage.
    """
    return order_price - effective_price
