import pandas as pd


def reconcile_trades(
    client_orders: pd.DataFrame, broker_trades: pd.DataFrame
) -> pd.DataFrame:
    """
    Match broker trades with client orders based on:
    - Symbol, Date, and Quantity Matching Logic.
    - Handles Exact Match, Partial Match, Excess Quantity, Pending Orders.
    - Allocates trades proportionally if multiple brokers are involved.

    Broker trades are first sorted by 'Buy/Sell Flag' and 'Cost'. The 'Buy/Sell Flag'
    ensures that Buy trades come before Sell trades, while 'Cost' organizes trades by price.
    This sorting order ensures that Buy orders are matched first, followed by Sell orders, with trades
    allocated based on price within each Buy or Sell group.

    After sorting, broker and client orders are grouped by symbol and date. These groups are then
    passed into reconciliation functions to ensure proper matching, allocation, and flagging of excess
    or pending orders.

    Returns:
        pd.DataFrame: A DataFrame containing reconciliation results including order status, matched quantities,
        unmatched quantities, total cost, and execution slippage.
    """
    client_orders["filled_qty"] = 0
    reconciled_trades = []

    broker_trades = broker_trades.sort_values(
        by=["buy_sell", "cost"], ascending=[True, True]
    )

    grouped_data = group_orders_and_trades(client_orders, broker_trades)

    for (isin, date), (client_group, broker_group) in grouped_data.items():
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
        dict: A dictionary where keys are tuples of (symbol, order_date) and values are tuples of
              (client_group, broker_group).
    """
    client_grouped = client_orders.groupby(by=["isin", "order_date"])
    broker_grouped = broker_trades.groupby(by=["isin", "deal_date"])

    grouped_data = {}
    for (isin, date), client_group in client_grouped:
        if (isin, date) in broker_grouped.groups:
            broker_group = broker_grouped.get_group((isin, date))
            grouped_data[(isin, date)] = (client_group, broker_group)

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
    reconciled_trades = []
    for _, trade in broker_group.iterrows():
        quantity, price, broker_fee, stt = (
            trade["quantity"],
            trade["cost"],
            trade["brokerage"],
            trade["stt"],
        )

        matching_orders = client_group[
            (client_group["filled_qty"] < client_group["quantity"])
        ]

        for _, order in matching_orders.iterrows():
            remaining_qty = order["quantity"] - order["filled_qty"]
            if quantity <= remaining_qty:
                reconciled_trades.append(
                    match_order_to_trade(
                        order, symbol, quantity, price, broker_fee, stt
                    )
                )
                break
            else:
                reconciled_trades.append(
                    partial_match_order_to_trade(
                        order, symbol, remaining_qty, quantity, price, broker_fee, stt
                    )
                )
                quantity -= remaining_qty

        if quantity > 0:
            reconciled_trades.append(
                excess_trade(symbol, quantity, price, broker_fee, stt)
            )

    return reconciled_trades


def match_order_to_trade(
    order, symbol: str, matched_qty: int, price: float, broker_fee: float, stt: float
) -> dict:
    """
    Creates a reconciliation result for an exact match of an order with a trade.

    Args:
        order (pd.Series): The client order.
        symbol (str): The symbol of the order.
        matched_qty (int): The quantity matched.
        price (float): The price at which the trade occurred.
        broker_fee (float): The broker's fee.
        stt (float): The securities transaction tax.

    Returns:
        dict: A reconciliation result.
    """
    total_cost = calculate_total_cost(price, matched_qty, broker_fee, stt)
    execution_slippage = calculate_execution_slippage(
        order["order_price"], price, matched_qty
    )
    return create_reconciliation_result(
        order, symbol, matched_qty, 0, "matched", total_cost, execution_slippage
    )


def partial_match_order_to_trade(
    order,
    symbol: str,
    matched_qty: int,
    remaining_qty: int,
    price: float,
    broker_fee: float,
    stt: float,
) -> dict:
    """
    Creates a reconciliation result for a partial match of an order with a trade.

    Args:
        order (pd.Series): The client order.
        symbol (str): The symbol of the order.
        matched_qty (int): The quantity matched.
        remaining_qty (int): The quantity remaining after partial matching.
        price (float): The price at which the trade occurred.
        broker_fee (float): The broker's fee.
        stt (float): The securities transaction tax.

    Returns:
        dict: A reconciliation result.
    """
    total_cost = calculate_total_cost(price, matched_qty, broker_fee, stt)
    execution_slippage = calculate_execution_slippage(
        order["order_price"], price, matched_qty
    )
    return create_reconciliation_result(
        order,
        symbol,
        matched_qty,
        remaining_qty,
        "partial",
        total_cost,
        execution_slippage,
    )


def excess_trade(
    symbol: str, excess_qty: int, price: float, broker_fee: float, stt: float
) -> dict:
    """
    Creates a reconciliation result for an excess quantity of trade that doesn't match any client order.

    Args:
        symbol (str): The symbol of the trade.
        excess_qty (int): The excess quantity that couldn't be matched with any client order.
        price (float): The price at which the trade occurred.
        broker_fee (float): The broker's fee.
        stt (float): The securities transaction tax.

    Returns:
        dict: A reconciliation result.
    """
    total_cost = calculate_total_cost(price, excess_qty, broker_fee, stt)
    return create_reconciliation_result(
        None, symbol, 0, excess_qty, "excess", total_cost, None
    )


def create_reconciliation_result(
    order,
    symbol: str,
    matched_quantity: int,
    unmatched_quantity: int,
    status: str,
    total_cost: float,
    execution_slippage: float,
) -> dict:
    """
    Creates a reconciliation result entry.

    Args:
        order (pd.Series or None): The client order, or None for excess trades.
        symbol (str): The symbol of the order or trade.
        matched_quantity (int): The quantity of the trade matched.
        unmatched_quantity (int): The quantity of the trade not matched.
        status (str): The status of the reconciliation (e.g., 'matched', 'partial', 'excess').
        total_cost (float): The total cost of the matched trade.
        execution_slippage (float): The execution slippage for the matched trade.

    Returns:
        dict: The reconciliation result.
    """
    return {
        "order_id": order["order_id"] if order is not None else None,
        "client_id": order["client_id"] if order is not None else None,
        "symbol": symbol,
        "matched_quantity": matched_quantity,
        "unmatched_quantity": unmatched_quantity,
        "status": status,
        "total_cost": total_cost,
        "execution_slippage": execution_slippage,
    }


def calculate_total_cost(
    price: float, quantity: int, broker_fee: float, stt: float
) -> float:
    return price * quantity + broker_fee + stt


def calculate_execution_slippage(
    order_price: float, price: float, quantity: int
) -> float:
    return order_price - (price / quantity)
