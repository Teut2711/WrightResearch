from pydantic import BaseModel
from datetime import date


class ClientOrder(BaseModel):
    order_id: str
    client_id: str
    symbol: str
    quantity: int
    order_price: float
    order_date: date


class BrokerTrade(BaseModel):
    deal_date: date
    party_code: str
    instrument: str
    isin: str
    buy_sell_flag: str
    quantity: int
    cost: float
    net_amount: float
    brokerage_amount: float
    settlement_date: date
    stt: float
    exchange_code: str
    depository_code: str


class ReconciliationResult(BaseModel):
    order_id: str
    client_id: str
    symbol: str
    matched_quantity: int
    unmatched_quantity: int
    status: str
    total_cost: float
    execution_slippage: float
